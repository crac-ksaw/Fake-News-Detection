import sys
from loguru import logger

logger.configure(
    handlers=[
        {"sink": sys.stdout, "level": "INFO", "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"},
        {"sink": "logs/app.log", "level": "DEBUG", "rotation": "10 MB", "retention": "10 days", "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"}
    ]
)
