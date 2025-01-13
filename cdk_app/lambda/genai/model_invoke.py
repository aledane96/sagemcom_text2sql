import json
import boto3
import logging
import os
from utils import bedrock_call, get_secret, generate_schema_string, execute_sql, build_response


RDS_DB_NAME = os.environ["RDS_DB_NAME"]
SECRET_RDS_DB_NAME = os.environ["SECRET_RDS_DB_NAME"]
BEDROCK_PARAMS = json.loads(os.environ["BEDROCK_PARAMS"]) 
AWS_REGION = os.environ["AWS_REGION"]

# Global parameters
logger = logging.getLogger()
logger.setLevel(level=logging.INFO)

def lambda_handler(event, context):
    
    print("--------------- LAUNCHING MODEL INVOKE LAMBDA -----------------")
    logger.info("--------------- LAUNCHING MODEL INVOKE LAMBDA -----------------")

    print(f"event: {event}")
    try:
        body = json.loads(event.get("body", "{}"))
        print(f"body: {body}")
        user_question = body.get("question", "").strip()

        if not user_question:
            raise ValueError("The 'question' field is required in the request body.")
    except Exception as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }

    # Print
    print(f"Model Config: {BEDROCK_PARAMS}")

    # Get secret param for RDS db 
    secret_rds = get_secret(AWS_REGION,SECRET_RDS_DB_NAME)
    secret_rds = json.loads(secret_rds)

    # Generate schema and feed it to tho model alongside the user's question to generate query
    schema = generate_schema_string(secret_rds)

    # Bedrock call
    print("Invoking Bedrock...")
    response = bedrock_call(AWS_REGION, user_question, BEDROCK_PARAMS, schema)
    print(f"Bedrock response: {response}")
    sql_query = json.loads(response.get('body')).get("result")
    print(f"The generated query is: {sql_query}")

    # RDS call
    print("Executing the generated query on RDS...")
    query_results = execute_sql(sql_query=sql_query, secret=secret_rds)

    print(f"query result from RDS: {query_results}")

    return build_response(
        {
            "sql_query": sql_query, #str
            "query_results": query_results #Dict
        }
    )
