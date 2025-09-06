"""
Logging configuration and utilities.

This module provides centralized logging configuration and utilities
for the Business Central MCP server.
"""

import logging
import os
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LoggingConfig:
  """Logging configuration."""

  level: str = "INFO"
  format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  log_file: Optional[str] = None

  @classmethod
  def from_environment(cls) -> "LoggingConfig":
    """
    Load logging configuration from environment variables.

    Environment variables:
    - LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - LOG_FORMAT: Custom log format string
    - LOG_FILE: Path to log file (optional, enables file logging)
    - MCP_VERBOSE: Set to 'true' to show INFO logs in Cursor (shows as [error])
    """
    # Avoid dotenv import to keep logging lightweight and independent
    level = os.getenv("LOG_LEVEL", "INFO")
    log_format = os.getenv("LOG_FORMAT", cls.format)
    log_file = os.getenv("LOG_FILE")
    return cls(level=level, format=log_format, log_file=log_file)


def setup_logging(config: Optional[LoggingConfig] = None) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        config: Logging configuration. If None, loads from environment.
    """
    if config is None:
        config = LoggingConfig.from_environment()
    
    # Configure root logger
    root_logger = logging.getLogger()
    
    # For MCP servers, we only want to show ERROR and CRITICAL levels to stderr
    # This prevents INFO/DEBUG logs from showing as [error] in Cursor
    root_logger.setLevel(logging.ERROR)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(config.format)
    
    # Console handler for errors only - Use stderr for MCP compatibility
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.ERROR)  # Only show actual errors in Cursor
    root_logger.addHandler(console_handler)
    
    # File handler for all levels if configured
    if config.log_file:
        try:
            file_handler = logging.FileHandler(config.log_file)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(getattr(logging, config.level.upper(), logging.INFO))
            root_logger.addHandler(file_handler)
        except Exception:
            # Silently fail file logging setup
            pass
    
    # Completely silence framework loggers
    framework_loggers = ['mcp', 'urllib3', 'requests', 'aiohttp', 'asyncio', 'msal']
    for logger_name in framework_loggers:
        framework_logger = logging.getLogger(logger_name)
        framework_logger.setLevel(logging.CRITICAL)
        framework_logger.disabled = True


def enable_verbose_logging() -> None:
    """
    Enable verbose logging to stderr for debugging purposes.
    
    Call this function when you want to see INFO/DEBUG logs in Cursor.
    Note: This will cause INFO logs to appear as [error] in Cursor logs.
    """
    root_logger = logging.getLogger()
    
    # Find the console handler and lower its level
    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stderr:
            handler.setLevel(logging.INFO)
            root_logger.setLevel(logging.INFO)
            break


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
