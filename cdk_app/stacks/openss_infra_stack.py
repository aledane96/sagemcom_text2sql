from constructs import Construct

import aws_cdk as core
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_ssm as ssm,
    aws_ecr as ecr
)
from aws_cdk import custom_resources as cr
from aws_cdk.aws_iam import (
    ServicePrincipal,
)
from aws_cdk.aws_lambda import (
    Tracing,
)
from aws_cdk.aws_logs import RetentionDays, LogGroup
from aws_cdk.aws_opensearchserverless import (
    CfnAccessPolicy,
    CfnCollection,
    CfnSecurityPolicy,
)

from aws_cdk import (
    Duration,
    RemovalPolicy,
)

import json
from aws_cdk.aws_ecr_assets import DockerImageAsset


class OpenSearchServerless(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        region: str,
        account_id: str,
        resource_prefix: str,
        collection_name: str,
        index_name: str,
        embedding_model_id: str
    ) -> None:
        super().__init__(scope, construct_id, env={
            'region': region,
            'account': account_id
        })

        self.resource_prefix = resource_prefix

        # The code that defines your stack goes here
        self.encryptionPolicy = self.create_encryption_policy(collection_name)
        self.networkPolicy = self.create_network_policy(collection_name)
        self.dataAccessPolicy = self.create_data_access_policy(collection_name)
        self.collection = self.create_collection(collection_name)

        # Create all policies before creating the collection
        self.networkPolicy.node.add_dependency(self.encryptionPolicy)
        self.dataAccessPolicy.node.add_dependency(self.networkPolicy)
        self.collection.node.add_dependency(self.encryptionPolicy)

        # # create an SSM parameters which store export values
        ssm.StringParameter(
            self,
            "collectionArn",
            parameter_name="/startwithkb/collectionArn",
            string_value=self.collection.attr_arn,
        )

        self.create_oss_index(index_name, embedding_model_id)

    def create_encryption_policy(self, collection_name) -> CfnSecurityPolicy:
        return CfnSecurityPolicy(
            self,
            "EncryptionPolicy",
            name=f"{collection_name}-enc",
            type="encryption",
            policy=json.dumps(
                {
                    "Rules": [
                        {
                            "ResourceType": "collection",
                            "Resource": [f"collection/{collection_name}"],
                        }
                    ],
                    "AWSOwnedKey": True,
                }
            ),
        )

    def create_network_policy(self, collection_name) -> CfnSecurityPolicy:
        return CfnSecurityPolicy(
            self,
            "NetworkPolicy",
            name=f"{collection_name}-net",
            type="network",
            policy=json.dumps(
                [
                    {
                        "Description": "Public access for ct-kb-aoss-collection collection",
                        "Rules": [
                            {
                                "ResourceType": "dashboard",
                                "Resource": [f"collection/{collection_name}"],
                            },
                            {
                                "ResourceType": "collection",
                                "Resource": [f"collection/{collection_name}"],
                            },
                        ],
                        "AllowFromPublic": True,
                    }
                ]
            ),
        )

    def create_collection(self, collection_name) -> CfnCollection:
        return CfnCollection(
            self,
            "Collection",
            name=collection_name,
            description=f"{collection_name}-repRAG-collection",
            type="VECTORSEARCH",
        )

    def create_data_access_policy(self, collection_name) -> CfnAccessPolicy:
        kbRoleArn = ssm.StringParameter.from_string_parameter_attributes(
            self, "kbRoleArn", parameter_name="/startwithkb/kbRoleArn"
        ).string_value
        return CfnAccessPolicy(
            self,
            "DataAccessPolicy",
            name=f"{collection_name}access",
            type="data",
            policy=json.dumps(
                [
                    {
                        "Rules": [
                            {
                                "Resource": [f"collection/{collection_name}"],
                                "Permission": [
                                    "aoss:CreateCollectionItems",
                                    "aoss:UpdateCollectionItems",
                                    "aoss:DescribeCollectionItems",
                                ],
                                "ResourceType": "collection",
                            },
                            {
                                "ResourceType": "index",
                                "Resource": [f"index/{collection_name}/*"],
                                "Permission": [
                                    "aoss:CreateIndex",
                                    "aoss:DescribeIndex",
                                    "aoss:ReadDocument",
                                    "aoss:WriteDocument",
                                    "aoss:UpdateIndex",
                                    "aoss:DeleteIndex",
                                ],
                            },
                        ],
                        "Principal": [kbRoleArn],
                    }
                ]
            ),
        )

    def create_oss_index(self, index_name, embedding_model_id):
        # dependency layer (includes requests, requests-aws4auth,opensearch-py, aws-lambda-powertools)

        oss_lambda_role = iam.Role(
            self,
            "OSSLambdaRole",
            assumed_by=ServicePrincipal("lambda.amazonaws.com"),
        )

        oss_lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "aoss:APIAccessAll",
                    "aoss:List*",
                    "aoss:Get*",
                    "aoss:Create*",
                    "aoss:Update*",
                    "aoss:Delete*",
                ],
                resources=["*"],
            )
        )


        # Reference an existing ECR repository and tag
        ecr_repository = ecr.Repository.from_repository_arn(
            self,
            "EcrKbOSS",
            repository_arn=f"arn:aws:ecr:{self.region}:{self.account}:repository/{self.resource_prefix}_kb_oss",
        )
        image_tag = "latest"


        oss_index_creation_lambda = _lambda.DockerImageFunction(
            self,
            "BKB-OSS-InfraSetupLambda",
            function_name=f"BKB-OSS-{index_name}-InfraSetupLambda",
            code=_lambda.DockerImageCode.from_ecr(
                repository=ecr_repository,
                tag=image_tag,
                cmd=["lambdas.bedrock_kb_lambda.oss_handler.lambda_handler"],
            ),
            role=oss_lambda_role,
            memory_size=1024,
            timeout=Duration.minutes(14),
            tracing=Tracing.ACTIVE,
            current_version_options={"removal_policy": RemovalPolicy.DESTROY},
            # environment={ #TODO: they are useless until now...
            #     "POWERTOOLS_SERVICE_NAME": "InfraSetupLambda",
            #     "POWERTOOLS_METRICS_NAMESPACE": "InfraSetupLambda-NameSpace",
            #     "POWERTOOLS_LOG_LEVEL": "INFO",
            # },
        )

        # Create a custom resource provider which wraps around the lambda above

        oss_provider_role = iam.Role(
            self,
            "OSSProviderRole",
            assumed_by=ServicePrincipal("lambda.amazonaws.com"),
        )
        oss_provider_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "aoss:APIAccessAll",
                    "aoss:List*",
                    "aoss:Get*",
                    "aoss:Create*",
                    "aoss:Update*",
                    "aoss:Delete*",
                ],
                resources=["*"],
            )
        )

        oss_index_creation_provider = cr.Provider(
            self,
            "OSSProvider",
            on_event_handler=oss_index_creation_lambda,
            log_group=LogGroup(
                self, "OSSIndexCreationProviderLogs", retention=RetentionDays.ONE_DAY
            ),
            role=oss_provider_role,
        )

        # Create a new custom resource consumer
        index_creation_custom_resource = core.CustomResource(
            self,
            "OSSIndexCreationCustomResource",
            service_token=oss_index_creation_provider.service_token,
            properties={
                "collection_endpoint": self.collection.attr_collection_endpoint,
                "data_access_policy_name": self.dataAccessPolicy.name,
                "index_name": index_name,
                "embedding_model_id": embedding_model_id,
            },
        )

        index_creation_custom_resource.node.add_dependency(oss_index_creation_provider)
