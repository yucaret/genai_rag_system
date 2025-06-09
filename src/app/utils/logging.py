import os
import logging
from config.logging_config import LOGGING_CONFIG, LOG_DIR
from logging.config import dictConfig

def init_logger():
    os.makedirs(LOG_DIR, exist_ok=True)
    dictConfig(LOGGING_CONFIG)
    return logging.getLogger("genai")
