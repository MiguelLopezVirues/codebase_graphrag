import logging
from src.utils.config.config import LOG_LEVEL, LOG_FILE

log_dir = LOG_FILE.parent
log_dir.mkdir(parents=True, exist_ok=True)

# Log everything to log file
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(LOG_LEVEL)  

# On console, only log errors
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.ERROR) 

# Configure logging with both handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logging.basicConfig(level=LOG_LEVEL, handlers=[file_handler, stream_handler])

logger = logging.getLogger(__name__)
