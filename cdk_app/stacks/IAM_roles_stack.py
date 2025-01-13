from aws_cdk import (
    Stack,
    aws_iam as iam,
)
from constructs import Construct

class IAMRoles(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # IAM Policies for Lambdas
        self.model_invoke_lambda_role = iam.Role(
            self,
            "ModelInvokeLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ],
        )

        # Add Bedrock-specific permissions
        bedrock_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["bedrock:*"],
            resources=["*"],
        )

        self.model_invoke_lambda_role.add_to_principal_policy(bedrock_policy)

        # Add permissions for RDS MySQL access
        rds_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "rds:Connect",
                "rds:DescribeDBInstances",
                "rds:DescribeDBClusters",
            ],
            resources=["*"], 
        )

        self.model_invoke_lambda_role.add_to_principal_policy(rds_policy)

        # Add permissions for Secrets Manager
        sm_policy = iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue"],
                resources=[
                    "*"
                ],#arn:aws:secretsmanager:eu-central-1:555043101106:secret:test-local-db
            )
        
        self.model_invoke_lambda_role.add_to_principal_policy(sm_policy)
            

        # Api Gateway Role
        self.api_logging_role = iam.Role(
            self,
            "ApiGatewayLoggingRole",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonAPIGatewayPushToCloudWatchLogs"
                )
            ],
        )

    def get_model_invoke_lambda_role(self) -> iam.Role:
        return self.model_invoke_lambda_role

    def get_api_logging_role(self) -> iam.Role:
        return self.api_logging_role
