"""
Logging utilities for CausalLLM
"""
import logging
from typing import Optional


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Get a logger with the given name."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    return logger


def get_structured_logger(name: str) -> 'StructuredLogger':
    """Get a structured logger."""
    return StructuredLogger(name)


class StructuredLogger:
    """Structured logger for CausalLLM."""
    
    def __init__(self, name: str):
        """Initialize structured logger."""
        self.name = name
        self.logger = logging.getLogger(name)
    
    def log_interaction(self, event: str, data: dict):
        """Log an interaction event."""
        self.logger.debug(f"{event}: {data}")
    
    def log_error(self, error: Exception, context: Optional[dict] = None):
        """Log an error with context."""
        self.logger.error(f"Error in {self.name}: {error}")
        if context:
            self.logger.error(f"Context: {context}")


def setup_package_logging(level="INFO", log_to_file=False, json_format=False):
    """Set up package-level logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )