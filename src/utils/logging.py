"""
Logging configuration for the travel planning system.
"""
import logging
import sys
from typing import Optional
from .config import config

def setup_logging(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Set up logging for a module.
    
    Args:
        name: Logger name (usually __name__)
        level: Optional log level override
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set level
    log_level = level or config.LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Avoid duplicate handlers
    if not logger.handlers:
        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
