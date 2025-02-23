from dotenv import load_dotenv, find_dotenv
import os
from pathlib import Path

dotenv_file = find_dotenv()
load_dotenv(dotenv_file)

# Base directory (set via environment or default value)
BASE_DIR = Path(os.getenv('PROJECT_ROOT_FOLDER',""))

# Neo4j connection settings
NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASS', 'your_password')

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
LOG_FILE = BASE_DIR / 'logs' / 'app.log'


# API Keys
OPENAI_API_KEY= os.getenv('OPENAI_API_KEY')