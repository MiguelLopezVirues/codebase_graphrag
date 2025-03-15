import logging
from src.utils.config.config import config
from src.utils.config.utils import get_log_level

log_dir = config["LOG_FILE"].parent
log_dir.mkdir(parents=True, exist_ok=True)

# Log everything to log file
file_handler = logging.FileHandler(config["LOG_FILE"])
file_level = get_log_level(config.get("LOG_LEVEL_FILE", "DEBUG"))
file_handler.setLevel(file_level)

# On console, only log errors
stream_handler = logging.StreamHandler()
stream_level = get_log_level(config.get("LOG_LEVEL_CONSOLE", "DEBUG"))
stream_handler.setLevel(stream_level)

# Configure logging with both handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(file_level)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
