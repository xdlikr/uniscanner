"""
Config Loader
配置加载器

Responsible for loading runtime configuration, distinct from constitution configuration.
负责加载运行时配置，区分于宪法配置。
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class RuntimeConfig(BaseModel):
    """Runtime Configuration / 运行时配置"""
    
    # System Mode / 系统模式
    system_mode: str = Field(default="SIMULATION", description="System Operation Mode / 系统运行模式")
    
    # Log Configuration / 日志配置
    log_level: str = Field(default="INFO", description="Log Level / 日志级别")
    log_dir: Path = Field(default=Path("logs"), description="Log Directory / 日志目录")
    
    # Constitution Path / 宪法路径
    constitution_path: Path = Field(default=Path("constitution.yaml"), description="Constitution File Path / 宪法文件路径")
    
    # Data Configuration / 数据配置
    data_dir: Optional[Path] = Field(default=None, description="Data Directory / 数据目录")
    
    # API Configuration / API配置
    broker_api_key: Optional[str] = Field(default=None, description="Broker API Key / 券商API密钥")
    broker_api_secret: Optional[str] = Field(default=None, description="Broker API Secret / 券商API密钥")
    llm_api_key: Optional[str] = Field(default=None, description="LLM API Key / LLM API密钥")
    
    # Environment / 环境标识
    environment: str = Field(default="development", description="Running Environment / 运行环境")
    
    model_config = ConfigDict(extra="allow")


class ConfigLoader:
    """Config Loader / 配置加载器"""
    
    def __init__(self, env_file: Optional[Path] = None):
        """
        Initialize Config Loader / 初始化配置加载器
        
        Args:
            env_file: .env file path, default is .env in current directory
        """
        self.env_file = env_file or Path(".env")
        self._config: Optional[RuntimeConfig] = None
    
    def load(self) -> RuntimeConfig:
        """
        Load Runtime Configuration / 加载运行时配置
        
        Returns:
            RuntimeConfig: Runtime configuration object
        """
        logger.info("Start loading runtime configuration / 开始加载运行时配置")
        
        # Load .env file / 加载.env文件
        if self.env_file.exists():
            load_dotenv(self.env_file)
            logger.info(f"Loaded environment file: {self.env_file} / 已加载环境文件")
        else:
            logger.warning(f"Environment file not found: {self.env_file}, using defaults / 环境文件不存在，使用默认配置")
        
        # Build config from environment variables / 从环境变量构建配置
        config_data = {
            "system_mode": os.getenv("SYSTEM_MODE", "SIMULATION"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "log_dir": Path(os.getenv("LOG_DIR", "logs")),
            "constitution_path": Path(os.getenv("CONSTITUTION_PATH", "constitution.yaml")),
            "data_dir": Path(os.getenv("DATA_DIR")) if os.getenv("DATA_DIR") else None,
            "broker_api_key": os.getenv("BROKER_API_KEY"),
            "broker_api_secret": os.getenv("BROKER_API_SECRET"),
            "llm_api_key": os.getenv("LLM_API_KEY"),
            "environment": os.getenv("ENVIRONMENT", "development"),
        }
        
        self._config = RuntimeConfig(**config_data)
        logger.info(f"Config loaded: mode={self._config.system_mode}, env={self._config.environment} / 配置加载完成")
        
        return self._config
    
    @property
    def config(self) -> RuntimeConfig:
        """
        Get current configuration / 获取当前配置
        
        Returns:
            RuntimeConfig: Configuration object
            
        Raises:
            RuntimeError: If config is not loaded
        """
        if self._config is None:
            raise RuntimeError("Config not loaded, please call load() method first / 配置尚未加载，请先调用 load() 方法")
        return self._config
    
    def get(self, key: str, default: any = None) -> any:
        """
        Get configuration item / 获取配置项
        
        Args:
            key: Configuration key
            default: Default value
            
        Returns:
            Configuration value
        """
        return getattr(self.config, key, default)
    
    def is_production(self) -> bool:
        """
        Check if production environment / 判断是否为生产环境
        
        Returns:
            bool: Whether is production environment
        """
        return self.config.environment.lower() in ["production", "prod"]
    
    def is_live_mode(self) -> bool:
        """
        Check if live mode / 判断是否为实盘模式
        
        Returns:
            bool: Whether is live mode
        """
        return self.config.system_mode == "LIVE"
