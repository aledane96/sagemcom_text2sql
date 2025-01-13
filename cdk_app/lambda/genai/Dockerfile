FROM public.ecr.aws/lambda/python:3.11

# Install any required dependencies here
ARG version=1.0
COPY requirements.txt . 
COPY model_invoke.py ${LAMBDA_TASK_ROOT}/
COPY utils.py ${LAMBDA_TASK_ROOT}/

RUN yum update -y

# Install dependencies from requirements.txt
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Install aws-lambda-rie for local testing (Runtime Interface Emulator)
COPY aws-lambda-rie /usr/local/bin/aws-lambda-rie

# Copy the entry script that is responsible for invoking the lambda handler
COPY entry_script.sh /entry_script.sh
RUN chmod +x /entry_script.sh

# Set the command to run the entry script
ENTRYPOINT ["/entry_script.sh"]

# Set default CMD if no custom command is provided
CMD ["model_invoke.lambda_handler"]
