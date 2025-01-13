import json
import os

from aws_cdk import (
    aws_iam as iam,
    aws_sqs as sqs,
    aws_kms as kms,
    RemovalPolicy,
    Stack,
    Duration,
)

import re


class ConventionNamingManager:

    def __init__(self):
        pass

    @staticmethod
    def get_s3_bucket_name_convention(
        *, stack: Stack, resource_prefix: str, envname: str, bucket_name: str
    ) -> str:
        import re

        pattern = r"^[a-z0-9]([a-z0-9\-]{0,18}[a-z0-9])?$"
        match = re.match(pattern, bucket_name)
        if match:
            return f"{resource_prefix}-{envname}-{stack.account}-{stack.region}-{bucket_name}"
        else:
            raise Exception(f"Invalid bucket name: {bucket_name}")

    @staticmethod
    def get_lambda_name_convention(
        resource_prefix: str, envname: str, lambda_name: str
    ) -> str:
        import re

        pattern = r"^[a-z0-9]([a-z0-9\-]{0,18}[a-z0-9])?$"
        match = re.match(pattern, lambda_name)
        if match:
            return f"{resource_prefix}-{envname}-{lambda_name}"
        else:
            raise Exception(f"Invalid lambda name: {lambda_name}")

    @staticmethod
    def get_vpc_name_convention(
        resource_prefix: str, envname: str, vpc_name: str
    ) -> str:
        import re

        pattern = r"^[a-z0-9]([a-z0-9\-]{0,18}[a-z0-9])?$"
        match = re.match(pattern, vpc_name)
        if match:
            return f"{resource_prefix}-{envname}-{vpc_name}"
        else:
            raise Exception(f"Invalid VPC name: {vpc_name}")

    @staticmethod
    def get_dynamodb_name_convention(
        resource_prefix: str, envname: str, table_name: str
    ) -> str:
        import re

        pattern = r"^[a-zA-Z0-9_.-]{3,255}$"
        match = re.match(pattern, table_name)
        if match:
            return f"{resource_prefix}-{envname}-{table_name}"
        else:
            raise Exception(f"Invalid ddb name: {table_name}")

    @staticmethod
    def get_secret_name_convention(
        resource_prefix: str, envname: str, parameter_name: str
    ) -> str:

        pattern = r"^(?!.*\/\/)(?!.*--)(?!.*\.\.)(?!.*__)(?!.*-\.)(?!.*\.-)(?!.*\._)(?!.*_\.)[a-zA-Z0-9/_\.-]+(?<!/)(?<!-)(?<!\.)(?<!_)$"
        match = re.match(pattern, parameter_name)
        if match:
            return f"/{resource_prefix}/{envname}/infrastructure/{parameter_name}"
        else:
            raise Exception(f"Invalid Secret parameter_name name: {parameter_name}")

    @staticmethod
    def get_graphql_name_convention(
        resource_prefix: str, envname: str, api_name: str
    ) -> str:
        import re

        pattern = r"^[a-z0-9]([a-z0-9\-]{0,18}[a-z0-9])?$"
        match = re.match(pattern, api_name)
        if match:
            return f"{resource_prefix}-{envname}-{api_name}"
        else:
            raise Exception(f"Invalid graphql api name: {api_name}")

    @staticmethod
    def get_ssm_name_convention(
        resource_prefix: str, envname: str, parameter_name: str
    ) -> str:

        pattern = r"^(?!.*\/\/)(?!.*--)(?!.*\.\.)(?!.*__)(?!.*-\.)(?!.*\.-)(?!.*\._)(?!.*_\.)[a-zA-Z0-9/_\.-]+(?<!/)(?<!-)(?<!\.)(?<!_)$"
        match = re.match(pattern, parameter_name)
        if match:
            return f"/{resource_prefix}/{envname}/infrastructure/{parameter_name}"
        else:
            raise Exception(f"Invalid parameter_name name: {parameter_name}")
