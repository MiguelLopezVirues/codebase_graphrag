#!/bin/bash
# scripts/create_parameter_store.sh

# Exit on any error
set -e

# Load variables from .env file if it exists
if [ -f .env ]; then
  echo "Loading environment variables from .env file..."
  export $(grep -v '^#' .env | xargs)
else
  echo ".env file not found! Exiting."
  exit 1
fi


# Verify required variables are set
required_vars=(NEO4J_URI_AURADB NEO4J_USER_AURADB NEO4J_PASS_AURADB OPENAI_API_KEY AWS_REGION)
for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "Error: $var is not set in .env file. Exiting."
    exit 1
  fi
done

# Create Parameter Store entries
echo "Creating Parameter Store entries..."

aws ssm put-parameter \
  --name "/code-graph/neo4j/uri" \
  --value "${NEO4J_URI_AURADB}" \
  --type "String" \
  --overwrite \
  --region ${AWS_REGION}

aws ssm put-parameter \
  --name "/code-graph/neo4j/user" \
  --value "${NEO4J_USER_AURADB}" \
  --type "String" \
  --overwrite \
  --region ${AWS_REGION}

aws ssm put-parameter \
  --name "/code-graph/neo4j/password" \
  --value "${NEO4J_PASS_AURADB}" \
  --type "SecureString" \
  --overwrite \
  --region ${AWS_REGION}

aws ssm put-parameter \
  --name "/code-graph/openai/api-key" \
  --value "${OPENAI_API_KEY}" \
  --type "SecureString" \
  --overwrite \
  --region ${AWS_REGION}

echo "Parameter Store entries created successfully!"
