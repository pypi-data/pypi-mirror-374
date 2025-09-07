
import logging
import os

log_level = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def get_logger(name: str = None, level: str = None):
    logger = logging.getLogger(name if name else "Vuln KB")
    
    # If a specific level is passed, override the global level
    if level:
        logger.setLevel(level.upper())  # Ensure level is in uppercase (e.g., 'INFO', 'DEBUG', etc.)
    
    return logger