#!/bin/bash
# infra/aws/graph_builder/deploy.sh

echo "Running create_parameter_store.sh to ensure parameters are set..."
. ./scripts/create_parameter_store.sh

echo "Using ECR Repository: $ECR_REPOSITORY_NAME"
echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"

# Construct ECR repository URI
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}"

echo "Logging in to Amazon ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin ${ECR_URI}

# Ensure the ECR repository exists (if not, create it)
if ! aws ecr describe-repositories --repository-names "$ECR_REPOSITORY_NAME" --region $AWS_REGION >/dev/null 2>&1; then
  echo "ECR repository does not exist. Creating it..."
  if ! aws --no-cli-pager ecr create-repository --repository-name "$ECR_REPOSITORY_NAME" --region $AWS_REGION; then
  echo "Failed with exit code $?"
  else
    echo "Success!"
  fi
else
  echo "ECR repository exists."
fi


echo "Building Docker image..."
docker buildx build --platform linux/amd64 --provenance=false -f infra/aws/graph_builder/Dockerfile -t ${ECR_REPOSITORY_NAME} .

echo "Tagging Docker image..."
docker tag ${ECR_REPOSITORY_NAME}:latest ${ECR_URI}:latest

echo "Pushing Docker image to ECR..."
docker push ${ECR_URI}:latest

echo "Deploying CloudFormation stack..."
aws cloudformation create-stack --stack-name graph-builder-stack \
  --template-body file://infra/aws/graph_builder/cloudformation.yml \
  --capabilities CAPABILITY_NAMED_IAM

echo "Deployment completed successfully!"
