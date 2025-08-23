"""
<<<<<<< HEAD
Logger utility module
"""
import logging
from datetime import datetime

def setup_logging(name="TradingBot", level=logging.INFO):
    """Setup basic logging"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# Default logger
logger = setup_logging()

def log_info(message):
    logger.info(message)

def log_error(message):
    logger.error(message)

def log_warning(message):
    logger.warning(message)
=======
Complete logging utilities for TradingBot v1.0
Provides setup_logging and other logging functions required by strategies
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up logging configuration for the trading bot
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        format_string: Optional custom format string
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Default format
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                log_file or f'logs/trading_bot_{datetime.now().strftime("%Y%m%d")}.log',
                encoding='utf-8'
            )
        ]
    )
    
    logger = logging.getLogger('TradingBot')
    logger.info(f"Logging initialized at {level} level")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)

def set_log_level(level: str):
    """Set the logging level for all loggers"""
    logging.getLogger().setLevel(getattr(logging, level.upper()))

# Additional logging utilities that might be imported
class Logger:
    """Simple Logger class for compatibility"""
    def __init__(self, name: str = "TradingBot"):
        self.logger = logging.getLogger(name)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def debug(self, message: str):
        self.logger.debug(message)

# Create default logger instance
logger = Logger()

# Additional functions that might be imported
def create_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Create a new logger with specified name and level"""
    new_logger = logging.getLogger(name)
    new_logger.setLevel(getattr(logging, level.upper()))
    return new_logger

def configure_logging(config: dict):
    """Configure logging with dictionary config"""
    logging.config.dictConfig(config)

# Export all functions
__all__ = [
    'setup_logging', 'get_logger', 'set_log_level', 'Logger', 
    'logger', 'create_logger', 'configure_logging'
]
>>>>>>> 8f626e2ef1a5d0198eacb62ca49d93985fc3b2f3
