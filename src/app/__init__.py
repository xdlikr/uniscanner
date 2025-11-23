"""
应用核心模块 - 模式管理、日志系统等
"""

from .mode_manager import ModeManager, SystemMode
from .logging_setup import setup_logging, get_logger

__all__ = [
    "ModeManager",
    "SystemMode",
    "setup_logging",
    "get_logger",
]

