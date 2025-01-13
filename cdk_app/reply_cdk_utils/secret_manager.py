import logging
import os
import json
import boto3
from botocore.exceptions import ClientError

log = logging.getLogger(__name__)


def ns2d(**kwargs):
    return kwargs


class SecretManager:
    def __init__(self):
        #useless so far
        pass

    @staticmethod
    def client(region=None):
        service_name = "secretsmanager"
        if os.getenv("AWS_DEFAULT_PROFILE"):
            return boto3.Session(profile_name=os.getenv("AWS_DEFAULT_PROFILE")).client(service_name=service_name,
                                                                                       region_name=region)
        else:
            return boto3.Session().client(service_name=service_name,
                                          region_name=region)

    @staticmethod
    def get_secret_value(region=os.getenv("CDK_DEFAULT_REGION"), secret_id=None):
        if not secret_id:
            raise Exception('Parameter name is None')
        try:
            response = SecretManager.client(region=region).get_secret_value(
                SecretId=secret_id)
            secret_string = response['SecretString']
            secret_dict = json.loads(secret_string)
            return secret_dict
        except ClientError as e:
            raise Exception(f"Secret manager {secret_id} doest not exist")
