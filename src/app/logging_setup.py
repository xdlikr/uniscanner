"""
Logging System Setup
日志系统配置

Provides structured logging, audit records, and error tracking.
提供结构化日志、审计记录和错误追踪功能。
"""

import logging
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from enum import Enum


class LogLevel(str, Enum):
    """Log Level / 日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuditEventType(str, Enum):
    """Audit Event Type / 审计事件类型"""
    CONSTITUTION_LOADED = "constitution_loaded"
    CONSTITUTION_VALIDATION_FAILED = "constitution_validation_failed"
    MODE_SWITCHED = "mode_switched"
    MODE_SWITCH_DENIED = "mode_switch_denied"
    EMERGENCY_TRIGGERED = "emergency_triggered"
    RISK_LIMIT_VIOLATED = "risk_limit_violated"
    SYSTEM_STARTED = "system_started"
    SYSTEM_STOPPED = "system_stopped"


class StructuredFormatter(logging.Formatter):
    """Structured Log Formatter (JSON) / 结构化日志格式化器（JSON格式）"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON / 格式化日志记录为JSON"""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields / 添加额外字段
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data

        # Add exception info / 添加异常信息
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(log_data, ensure_ascii=False)


class AuditLogger:
    """Audit Logger / 审计日志记录器"""

    def __init__(self, log_dir: Path):
        """
        Initialize Audit Logger / 初始化审计日志记录器
        
        Args:
            log_dir: Log directory
        """
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create audit log file / 创建审计日志文件
        audit_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
        self.audit_file = audit_file
        
        # Configure audit logger / 配置审计logger
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        
        # File handler / 文件处理器
        file_handler = logging.FileHandler(audit_file, encoding="utf-8")
        file_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(file_handler)

    def log_event(
        self,
        event_type: AuditEventType,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
    ) -> None:
        """
        Record Audit Event / 记录审计事件
        
        Args:
            event_type: Event type
            message: Event message
            details: Event details
            user: Operating user
        """
        audit_data = {
            "event_type": event_type.value,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        if details:
            audit_data["details"] = details
        
        if user:
            audit_data["user"] = user
        
        # Use extra param to pass structured data / 使用extra参数传递结构化数据
        self.logger.info(
            f"[AUDIT] {event_type.value}: {message}",
            extra={"extra_data": audit_data}
        )


def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    enable_console: bool = True,
    enable_file: bool = True,
) -> AuditLogger:
    """
    Configure Global Logging System / 配置全局日志系统
    
    Args:
        log_level: Log level
        log_dir: Log directory, default is logs/
        enable_console: Whether to enable console output
        enable_file: Whether to enable file output
        
    Returns:
        AuditLogger: Audit logger instance
    """
    # Set log directory / 设置日志目录
    if log_dir is None:
        log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger / 配置根logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers / 清除现有处理器
    root_logger.handlers.clear()
    
    # Console handler (Human readable) / 控制台处理器（人类可读格式）
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)
    
    # File handler (Structured JSON) / 文件处理器（结构化JSON格式）
    if enable_file:
        log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # Log all levels to file / 文件记录所有级别
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)
    
    # Create audit logger / 创建审计日志记录器
    audit_logger = AuditLogger(log_dir)
    
    # Record system start / 记录系统启动
    audit_logger.log_event(
        AuditEventType.SYSTEM_STARTED,
        "Logging system initialized / 日志系统已初始化",
        details={"log_level": log_level, "log_dir": str(log_dir)}
    )
    
    return audit_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get logger by name / 获取指定名称的logger
    
    Args:
        name: Logger name, usually __name__
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)
