"""
Logger configuration with colored output and file logging
"""
import logging
import colorlog
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "SuperClearChat", level: str = "INFO", log_to_file: bool = True) -> logging.Logger:
    """
    Setup colored logger with custom format and optional file logging
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_to_file: Whether to log to file
    
    Returns:
        Configured logger instance
    """
    logger = colorlog.getLogger(name)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Set logging level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create console handler with colors
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Create colored formatter for console
    console_formatter = colorlog.ColoredFormatter(
        "%(white)s%(asctime)s%(reset)s | "
        "%(log_color)s%(levelname)-8s%(reset)s | "
        "%(white)s%(message)s%(reset)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if requested
    if log_to_file:
        # Create logs directory if it doesn't exist
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # Create rotating file handler
        log_file = os.path.join(logs_dir, f"{name.lower()}.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        
        # Create plain formatter for file (no colors)
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Log the file location
        logger.info(f"Logging to file: {os.path.abspath(log_file)}")
    
    # Prevent duplicate logs
    logger.propagate = False
    
    return logger

def reconfigure_logger_with_config(config) -> None:
    """
    Reconfigure the global logger with settings from config
    
    Args:
        config: Configuration object containing LOG_LEVEL and LOG_TO_FILE
    """
    global logger
    logger = setup_logger(
        name="SuperClearChat",
        level=config.LOG_LEVEL,
        log_to_file=config.LOG_TO_FILE
    )

def log_session_start() -> None:
    """Log session start information"""
    logger.info("=" * 80)
    logger.info("🚀 SuperClearChat Bot - Session Started")
    logger.info(f"📅 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

def log_session_end() -> None:
    """Log session end information"""
    logger.info("=" * 80)
    logger.info("🛑 SuperClearChat Bot - Session Ended")
    logger.info(f"📅 End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

# Create global logger instance (will be reconfigured after config is loaded)
logger = setup_logger(log_to_file=False)  # Initially without file logging
