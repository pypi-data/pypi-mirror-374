"""
Logging utilities for PyGenAI Security Framework
"""

import logging
import sys
import os
from pathlib import Path
from typing import Optional


def get_logger(name: str) -> logging.Logger:
    """Get configured logger for module"""
    return logging.getLogger(f'pygenai_security.{name}')


def setup_logging(
    level: str = 'INFO',
    log_file: Optional[str] = None,
    max_file_size: int = 100 * 1024 * 1024,  # 100MB
    backup_count: int = 5
):
    """Setup comprehensive logging system"""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger('pygenai_security')
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        from logging.handlers import RotatingFileHandler
        
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger
