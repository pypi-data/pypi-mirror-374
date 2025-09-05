"""
Logger utility for OpenFiles SDK

Uses OPENFILES_LOG environment variable for log level control:
- none (default): No logging
- error: Only errors
- info: Important operations + errors  
- debug: Everything (detailed flow)
"""

import os
from typing import Literal

LogLevel = Literal['none', 'error', 'info', 'debug']


class Logger:
    def __init__(self, prefix: str = '[OpenFiles]'):
        self.prefix = prefix
        env_level = os.environ.get('OPENFILES_LOG', '').lower()
        self.level: LogLevel = env_level if env_level in ['none', 'error', 'info', 'debug'] else 'none'
    
    def error(self, message: str) -> None:
        """Log errors (shown in error, info, and debug levels)"""
        if self.level in ['error', 'info', 'debug']:
            print(f"{self.prefix} ERROR: {message}")
    
    def info(self, message: str) -> None:
        """Log important information (shown in info and debug levels)"""
        if self.level in ['info', 'debug']:
            print(f"{self.prefix} {message}")
    
    def debug(self, message: str) -> None:
        """Log debug information (shown only in debug level)"""
        if self.level == 'debug':
            print(f"{self.prefix} [DEBUG] {message}")
    
    def success(self, operation: str, target: str, ms: int = None) -> None:
        """Log successful operations (shown in info and debug levels)"""
        if self.level in ['info', 'debug']:
            time_str = f" ({ms}ms)" if ms else ""
            print(f"{self.prefix} SUCCESS: {operation}: {target}{time_str}")
    
    def is_enabled(self, level: LogLevel) -> bool:
        """Check if a specific log level is enabled"""
        levels = ['none', 'error', 'info', 'debug']
        current_index = levels.index(self.level)
        check_index = levels.index(level)
        return current_index >= check_index


# Internal SDK logger - not exported to end users
logger = Logger()


# Legacy compatibility function
def get_logger(name: str, level: str = None) -> Logger:
    """
    Legacy compatibility function
    Returns the global logger instance
    """
    return logger
