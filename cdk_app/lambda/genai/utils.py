import boto3
import json
import os
import logging
import pymysql
import pandas as pd
from typing import Dict
import botocore.config
from botocore.exceptions import ClientError

from langchain.prompts import PromptTemplate
from langchain.llms import Bedrock
from langchain.chains import LLMChain
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser



def get_secret(aws_region, secret_name):
    secret_manager = boto3.client(service_name='secretsmanager', region_name=aws_region)
    try:
        get_secret_value_response = secret_manager.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    return secret




def generate_schema_string(secret):
    
    # Connection to db
    host=secret["host"]
    database=secret["dbname"]
    user=secret["username"]
    password=secret["password"]
    port=int(secret["port"])

    print(f"Trying to connect to RDS db {database} in the host {host}...")

    conn = pymysql.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=port
        )
    
    cur = conn.cursor()

    print("Connection estabilished!")

    
    # Query 1: Get all table and column details
    schema_query = f"""
    SELECT 
        c.table_name, c.column_name, c.data_type, c.is_nullable, c.column_default
    FROM 
        information_schema.columns c
    WHERE 
        c.table_schema = '{database}'
    ORDER 
        BY c.table_name, c.ordinal_position;
    """

    # Query 2: Get primary keys for each table
    primary_keys_query = f"""
    SELECT 
        kcu.table_name, kcu.column_name
    FROM 
        information_schema.table_constraints tc
    JOIN 
        information_schema.key_column_usage kcu
    ON 
        tc.constraint_name = kcu.constraint_name
    AND 
        tc.table_schema = kcu.table_schema
    WHERE 
        tc.constraint_type = 'PRIMARY KEY' AND tc.table_schema = '{database}';
    """

    # Query 3: Get foreign keys and references for each table
    foreign_keys_query = f"""
    SELECT 
        kcu.table_name AS referencing_table,
        kcu.column_name AS referencing_column,
        kcu.referenced_table_name AS referenced_table
    FROM 
        information_schema.key_column_usage AS kcu
    JOIN 
        information_schema.referential_constraints AS rc
    ON 
        kcu.constraint_name = rc.constraint_name
        AND kcu.table_schema = rc.constraint_schema
    WHERE 
        kcu.table_schema = '{database}';
    """

    # Execute the queries and fetch results
    cur.execute(schema_query)
    columns_details = cur.fetchall()

    cur.execute(primary_keys_query)
    primary_keys = cur.fetchall()

    cur.execute(foreign_keys_query)
    foreign_keys = cur.fetchall()

    # Organize details into dictionaries
    schema_dict = {}
    primary_keys_dict = {table: set() for table, _ in primary_keys}
    foreign_keys_dict = {table: {} for table, _, _ in foreign_keys}

    for table, column in primary_keys:
        primary_keys_dict[table].add(column)

    for table, column, ref_table in foreign_keys:
        foreign_keys_dict[table][column] = ref_table

    # Build the schema dictionary
    for table, column, data_type, is_nullable, column_default in columns_details:
        if table not in schema_dict:
            schema_dict[table] = []
        column_desc = f"{column} ({data_type.upper()}"

        # Add primary key annotation
        if column in primary_keys_dict.get(table, []):
            column_desc += ", PRIMARY KEY"

        # Add foreign key reference
        if column in foreign_keys_dict.get(table, {}):
            column_desc += f", FOREIGN KEY REFERENCES {foreign_keys_dict[table][column]}"

        column_desc += ")"
        schema_dict[table].append(column_desc)

    # Format the schema string
    schema_str = ""
    for table, columns in schema_dict.items():
        schema_str += f"{table}:\n"
        for col in columns:
            schema_str += f"- {col}\n"
        schema_str += "\n"

    return schema_str



def bedrock_call(aws_region, user_request, model_params, schema=None):
    # Create the client
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name=aws_region,
    )

    model_kwargs = { 
        "max_tokens": model_params["max_tokens"],
        "temperature": model_params["temperature"],
    }

    claude_3_client = ChatBedrock(
        client=bedrock_runtime,
        model_id=model_params["model_id"],
        model_kwargs=model_kwargs,
    )

    # Handle schema
    schema_info = schema if schema else "No schema provided."

    # Create a LangChain prompt template
    template = """
    Human: Transform the following natural language request into a valid MySQL query. Assume a database with the following tables and columns exists :
                {schema}
                \n\n
                Guidelines:
                - Return only the  executable SQL query without any explanation \n
                - Do not include any explanation in the SQL query \n
                - Do not include any extra text in the SQL query \n
                - Do not include  \ n to return to line in the SQL query : make it all in one line \n
                - Do not include any extra spaces in the SQL query \n
                The question is: {question} \n
                Assistant:
    """
    prompt = PromptTemplate(
        input_variables=["question", "schema"],
        template=template,
    )

    # Format the prompt with the user's question and schema
    final_prompt = prompt.format(question=user_request, schema=schema_info)


    print("------- Prompt Begin -------")
    print(final_prompt)
    print("------- Prompt End -------")
    
    # Invoke the chain
    messages = [
        ("human", "{question}"),
    ]

    chain_prompt = ChatPromptTemplate.from_messages(messages)
    chain = chain_prompt | claude_3_client | StrOutputParser()

    try:
        result = chain.invoke({"question": final_prompt})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error while invoking the chain: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error."})
        }

    # Return the response
    return build_response({"result":result})



def build_response(body: Dict) -> Dict:
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }


def execute_sql(sql_query: str, secret) -> dict:

    try:
        # Connect to the database
        conn = pymysql.connect(
            host=secret["host"],
            database=secret["dbname"],
            user=secret["username"],
            password=secret["password"],
            port=int(secret["port"])
        )
        
        # Execute the SQL query
        cur = conn.cursor()
        cur.execute(sql_query)
        result = cur.fetchall()
        
        # Transform data into a DataFrame and then into a dictionary
        column_names = [desc[0] for desc in cur.description]
        df = pd.DataFrame(result, columns=column_names)
        df = df.astype(str)
        result_dict = df.to_dict(orient='records')
        
        # Clean up
        cur.close()
        conn.close()
        
        return result_dict

    except Exception as e:
        # Return the error message to the main function
        return {"error": str(e)}