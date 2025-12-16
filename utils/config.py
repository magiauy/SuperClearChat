"""
Configuration handler for the bot
"""
import os
from typing import Optional
from dotenv import load_dotenv
from utils.logger import logger

class Config:
    """Configuration class to handle environment variables"""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Bot configuration
        self.DISCORD_TOKEN: Optional[str] = os.getenv('DISCORD_TOKEN')
        self.BOT_PREFIX: str = os.getenv('BOT_PREFIX', '!')
        
        # Limits configuration
        self.MAX_DAYS_LIMIT: int = int(os.getenv('MAX_DAYS_LIMIT', '14'))
        self.MIN_DAYS_LIMIT: int = int(os.getenv('MIN_DAYS_LIMIT', '1'))
        
        # Logging configuration
        self.LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_TO_FILE: bool = os.getenv('LOG_TO_FILE', 'true').lower() == 'true'
        
        # Validate required configuration
        self._validate_config()
        
        # Reconfigure logger with config settings
        self._reconfigure_logger()
    
    def _reconfigure_logger(self) -> None:
        """Reconfigure logger with config settings"""
        from utils.logger import reconfigure_logger_with_config
        reconfigure_logger_with_config(self)
    
    def _validate_config(self) -> None:
        """Validate required configuration values"""
        if not self.DISCORD_TOKEN:
            logger.error("DISCORD_TOKEN không được tìm thấy trong file .env")
            raise ValueError("DISCORD_TOKEN is required")
        
        if self.MAX_DAYS_LIMIT < self.MIN_DAYS_LIMIT:
            logger.error(f"MAX_DAYS_LIMIT ({self.MAX_DAYS_LIMIT}) không thể nhỏ hơn MIN_DAYS_LIMIT ({self.MIN_DAYS_LIMIT})")
            raise ValueError("MAX_DAYS_LIMIT must be greater than or equal to MIN_DAYS_LIMIT")
        
        logger.info("Cấu hình đã được tải thành công")
        logger.info(f"Bot Prefix: {self.BOT_PREFIX}")
        logger.info(f"Days Limit: {self.MIN_DAYS_LIMIT} - {self.MAX_DAYS_LIMIT}")
        logger.info(f"Log Level: {self.LOG_LEVEL}")
        logger.info(f"Log to File: {self.LOG_TO_FILE}")

# Create global config instance
config = Config()
