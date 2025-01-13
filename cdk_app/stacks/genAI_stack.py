from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_ecr as ecr,
    aws_logs as logs,
    aws_dynamodb as dynamodb,
    CfnOutput,
    RemovalPolicy,
    aws_ecr as ecr
)
from constructs import Construct
from reply_cdk_utils.ConventionNaming import ConventionNamingManager
import json

class genAI(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        resource_prefix: str,
        envname: str,
        region: str,
        account_id: str,
        rds_db_name:str,
        secret_rds_db_name: str,
        bedrock_params: dict,
        model_invoke_lambda_role:iam.Role,
        api_logging_role:iam.Role,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ############ LAMBDAS #################

        # Reference an existing ECR repository and tag
        ecr_repository = ecr.Repository.from_repository_arn(
            self,
            "ECRgenai",
            repository_arn=f"arn:aws:ecr:{region}:{account_id}:repository/{resource_prefix}",
        )
        image_tag = "genai"

        # Model Invoke Lambda
        model_invoke_lambda = _lambda.DockerImageFunction(
            self,
            f"ModelInvokeLambda{resource_prefix}",
            function_name=ConventionNamingManager.get_lambda_name_convention(
                resource_prefix=resource_prefix,
                envname=envname,
                lambda_name="model-invoke",
            ),
            code=_lambda.DockerImageCode.from_ecr(
                repository=ecr_repository,
                tag=image_tag,
                cmd=["model_invoke.lambda_handler"],
            ),
            memory_size=512,
            role=model_invoke_lambda_role,
            timeout=Duration.seconds(60),
            tracing=_lambda.Tracing.ACTIVE,
            environment={
                "RDS_DB_NAME": rds_db_name,
                "SECRET_RDS_DB_NAME": secret_rds_db_name,
                "BEDROCK_PARAMS": json.dumps(bedrock_params)
            }
        )


        ################ API GATEWAY AND CLOUDWATCH ##################

        # Enable logging for API Gateway
        # CloudWatch log group for API Gateway logs
        api_log_group = logs.LogGroup(
            self,
            f"ApiGatewayLogGroup{resource_prefix}",
            log_group_name="ApiGatewayLogs",
            removal_policy=RemovalPolicy.DESTROY
           # retention=logs.RetentionDays.ONE_WEEK
        )

        api = apigateway.RestApi(
            self,
            f"LangchainApi{resource_prefix}",
            rest_api_name="LangchainAPI",
            description="API Gateway to invoke Langchain Lambda",
            deploy_options=apigateway.StageOptions(
                logging_level=apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=True,  # Log request and response data
                tracing_enabled=True,
                access_log_destination=apigateway.LogGroupLogDestination(api_log_group),
                access_log_format=apigateway.AccessLogFormat.json_with_standard_fields(
                    caller=True,
                    http_method=True,
                    ip=True,
                    protocol=True,
                    request_time=True,
                    resource_path=True,
                    response_length=True,
                    status=True,
                    user=True,
                ),
            ),
        )

        # Set API Gateway logging role at account level
        apigateway.CfnAccount(
            self,
            f"ApiGatewayAccount{resource_prefix}",
            cloud_watch_role_arn=api_logging_role.role_arn,
        )

        # Define a Resource and Method
        langchain_resource = api.root.add_resource("invoke")
        langchain_resource.add_method("POST", apigateway.LambdaIntegration(model_invoke_lambda))

        # Output the API Gateway endpoint
        CfnOutput(
            self,
            f"LangchainApiEndpoint{resource_prefix}",
            value=f"{api.url}invoke",  # Append 'invoke' to the base URL
            description="The API Gateway endpoint for invoking the Langchain Lambda"
        )

