from dotenv import load_dotenv, find_dotenv
from src.utils.config.utils import get_ssm_parameter
import yaml
import os
from pathlib import Path

BASE_DIR = Path(__file__)

# Load environment variables
dotenv_file = find_dotenv()
load_dotenv(dotenv_file)

# Load prompts yaml
with open(Path(__file__).parent / "prompts.yaml", "r", encoding="utf-8") as f:
    prompts = yaml.safe_load(f)

config = {
    # Neo4j connection settings
    "NEO4J_URI": get_ssm_parameter("/codebase-rag/neo4j-uri", decription=False) or os.getenv("NEO4J_URI_AURADB", None),
    "NEO4J_USER": get_ssm_parameter("/codebase-rag/neo4j-user", decription=False) or os.getenv("NEO4J_USER_AURADB", None),
    "NEO4J_PASSWORD": get_ssm_parameter("/codebase-rag/neo4j-password", decription=True) or os.getenv("NEO4J_PASS_AURADB", None),
    "NEO4J_DATABASE": get_ssm_parameter("/codebase-rag/neo4j-database", decription=False) or os.getenv("NEO4J_DATABASE", "neo4j"),

    # Neo4j vector store details - DO NOT CHANGE OR DO WITH EXTREME CAUTION
    "VECTOR_INDEX_NAME": "code_embedding",
    "VECTOR_NODE_LABEL": "CodeEntity",
    "VECTOR_SOURCE_PROPERTY_CODE": "code",
    "VECTOR_SOURCE_PROPERTY_DOCS": "docstring",
    "VECTOR_EMBEDDING_PROPERTY": "code_embedding",

    # Retrieval prompts
    "ROUTER_PROMPT": prompts.get("ROUTER_PROMPT", ""),
    "GRAPH_AUGMENTED_SIMILARITY_QUERY": prompts.get("GRAPH_AUGMENTED_SIMILARITY_QUERY", ""),
    "VECTOR_QA_SYSTEM_PROMPT": prompts.get("VECTOR_QA_SYSTEM_PROMPT", ""),
    "CYPHER_GENERATION_TEMPLATE": prompts.get("CYPHER_GENERATION_TEMPLATE",""),
    "GRAPH_QA_GENERATION_TEMPLATE": prompts.get("GRAPH_QA_GENERATION_TEMPLATE",""),
    "CONVERSATIONAL_QA_SYSTEM_PROMPT": prompts.get("CONVERSATIONAL_QA_SYSTEM_PROMPT",""),

    # Logging configuration
    "LOG_LEVEL": "INFO",
    "LOG_LEVEL_CONSOLE": "ERROR",
    "LOG_FILE": Path("/tmp/logs/app.log") if os.getenv("AWS_EXECUTION_ENV") else Path(os.getenv("PROJECT_ROOT_FOLDER", str(BASE_DIR.parent.parent.parent.parent))) / "tmp" / "app.log",

    # API Keys
    "OPENAI_API_KEY": get_ssm_parameter("/codebase-rag/openai-api-key", decription=True) or os.getenv("OPENAI_API_KEY"),
}
