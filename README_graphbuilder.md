# Code Knowledge Graph Builder

This section of the project creates a knowledge graph from your code repository, stores it in Neo4j, and provides tools to interact with it.

## Architecture

- **Graph Builder**: Parses code and creates a Neo4j knowledge graph
- **API**: Handles file uploads and triggers graph building
- **Neo4j Database**: Stores the knowledge graph (uses Neo4j AuraDB cloud)

## Deployment Options

### Option 1: Run Locally (No Docker)

Requirements:
- Python 3.9+
- Neo4j credentials (can use AuraDB)
- OpenAI API key

Steps:
1. Clone the repository
2. Create a `.env` file with your credentials:
   ```
   NEO4J_URI=neo4j+s://your-db.auradb.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your-password
   OPENAI_API_KEY=your-api-key
   ```
3. Install dependencies:
   ```bash
   pip install poetry
   poetry install
   ```
4. Run the graph builder:
   ```bash
   python infra/local/run_local.py --file_path=/path/to/your/code
   ```

### Option 2: Run Locally with Docker

Requirements:
- Docker and Docker Compose
- Neo4j credentials (can use AuraDB)
- OpenAI API key

Steps:
1. Clone the repository
2. Create a `.env` file with your credentials (as above)
3. Run with Docker Compose:
   ```bash
   cd infra/local
   docker-compose up
   ```

### Option 3: Deploy to AWS Cloud

Requirements:
- AWS account
- AWS CLI configured locally
- Docker installed locally
- Neo4j credentials (can use AuraDB)
- OpenAI API key

Steps:
1. Clone the repository
2. Set up the AWS CLI and AWS account credentials.
3. Create Parameter Store entries:
   ```bash
   ./scripts/create_parameter_store.sh
   ```
4. Deploy the infrastructure:
   ```bash
   ./scripts/deploy_graph_builder.sh
   ```
5. Use the API URL from the output to upload code repositories

## Using the API

Once deployed, you can upload code repositories as ZIP files to the API:

```bash
curl -X POST \
  -F "file=@your-repo.zip" \
  https://your-api-url/upload
```

Or use the Streamlit interface which provides a user-friendly upload form.