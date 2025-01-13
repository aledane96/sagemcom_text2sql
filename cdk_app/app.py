#!/usr/bin/env python3
import os
import aws_cdk as cdk
#from stacks.ecr_stack import ECRStack
from stacks.IAM_roles_stack import IAMRoles
from stacks.genAI_stack import genAI
from stacks.openss_infra_stack import OpenSearchServerless

app = cdk.App()

# Config params
environment_configuration = app.node.try_get_context("DeploymentEnvironments").get(
    "dev"
)
print("environment_configuration",environment_configuration)
config = {
    "resource_prefix": f"{environment_configuration.get('RESOURCE_PREFIX')}",
    "account_id": f"{environment_configuration.get('ACCOUNT_ID')}",
    "cdk_region": f"{environment_configuration.get('REGION')}",
    "s3_bucket_name": f"{environment_configuration.get('S3_BUCKET_NAME')}",
    "tags": f"{environment_configuration.get('STACK-TAGS')}",
    "rds_db_name": f"{environment_configuration.get('RDS_DB_NAME')}",
    "secret_rds_db_name": f"{environment_configuration.get('SECRET_RDS_DB_NAME')}",
    "WORKSPACE_NAME": f"{environment_configuration.get('WORKSPACE_NAME')}",
    "bedrock_params" : {
            "model_id" : "eu.anthropic.claude-3-5-sonnet-20240620-v1:0",
            "max_tokens" : 512,
            "temperature" : 0.0
    },
    "EMBEDDING_MODEL_ID": ["amazon.titan-embed-text-v2:0"],
    "CHUNKING_STRATEGY": {
        0: "Default chunking",
        1: "Fixed-size chunking",
        2: "No chunking",
    },
    "MAX_TOKENS": 512,  # type: ignore
    "OVERLAP_PERCENTAGE": 20
}


envname = eval(config["tags"])["Environment"]
collection_name = f"{config['resource_prefix']}kbcollection"
index_name = f"{config['resource_prefix']}kbindex"
env = cdk.Environment(account=config['account_id'], region=config['cdk_region'])


## IAM Roles stack
iam_roles_stack = IAMRoles(app, 
                           "IAMRolesStack")


# ## OSS stack
# OpenSearchServerless(
#             app,
#             "OpenSearchServerlessStack",
#             region=config["cdk_region"],
#             account_id=config["account_id"],
#             resource_prefix=config["resource_prefix"],
#             collection_name=collection_name,
#             index_name=index_name,
#             embedding_model_id=config["EMBEDDING_MODEL_ID"][0]
#             )

## Lambda (Langchain) stack
genAI(app, 
            "genAIStack", 
            resource_prefix=config["resource_prefix"],
            envname=envname,
            region=config["cdk_region"],
            account_id=config["account_id"],
            rds_db_name=config["rds_db_name"],
            secret_rds_db_name=config["secret_rds_db_name"],
            bedrock_params = config["bedrock_params"],
            model_invoke_lambda_role=iam_roles_stack.get_model_invoke_lambda_role(),
            api_logging_role=iam_roles_stack.get_api_logging_role()
            )


app.synth()
