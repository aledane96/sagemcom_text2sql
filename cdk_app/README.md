# TEXT2SQL PROJECT for SAGEMCOM

## Executive Summary
In this project, we aim to empower Sagemcom technicians to seamlessly create Grafana dashboards by leveraging natural language to SQL transformation capabilities. This initiative is designed to eliminate the need for SQL expertise among technicians while providing them with the ability to query databases and generate visualizations efficiently.

## Stacks to be complited
1. IAM roles
2. OpenSearch Serverless stack: for the indexing and retrieval of tables metadata
3. Text2SQL Lambda stack: lambda which is connected to OSS and Bedrock for the text-to-sql transformation. It is connected to API Gateway as well.

## To add
1. Athena stack: for evaluating the enerated query and for connection.
