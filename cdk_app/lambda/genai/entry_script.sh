#!/bin/sh
# echo "Checking Python path"
# command -v python3
# echo "Python Version"
# python3 --version
if [ -z "${AWS_LAMBDA_RUNTIME_API}" ]; then
  # Run the Runtime Interface Emulator for local testing
  echo "Local execution"
  exec /usr/local/bin/aws-lambda-rie /var/lang/bin/python3 -m awslambdaric "$@"
else
  # Run the Lambda function normally
  echo "AWS execution"
  exec /var/lang/bin/python3 -m awslambdaric "$@"
fi
