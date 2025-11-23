"""
Constitution Loader
宪法加载器

Responsible for loading constitution configuration from YAML files and converting to Python objects.
负责从YAML文件加载宪法配置并转换为Python对象。
"""

import yaml
from pathlib import Path
from typing import Optional
import logging

from .schema import Constitution

logger = logging.getLogger(__name__)


class ConstitutionLoadError(Exception):
    """Constitution Load Error / 宪法加载错误"""
    pass


class ConstitutionLoader:
    """Constitution Loader / 宪法加载器"""

    def __init__(self, constitution_path: Optional[Path] = None):
        """
        Initialize Constitution Loader / 初始化宪法加载器
        
        Args:
            constitution_path: Path to constitution file, default is constitution.yaml
        """
        if constitution_path is None:
            constitution_path = Path("constitution.yaml")
        
        self.constitution_path = Path(constitution_path)
        self._constitution: Optional[Constitution] = None

    def load(self, validate: bool = True) -> Constitution:
        """
        Load Constitution Configuration / 加载宪法配置
        
        Args:
            validate: Whether to validate after loading
            
        Returns:
            Constitution: Constitution object
            
        Raises:
            ConstitutionLoadError: Raised when loading fails
        """
        try:
            logger.info(f"Start loading constitution file: {self.constitution_path}")
            
            # Check if file exists / 检查文件是否存在
            if not self.constitution_path.exists():
                raise ConstitutionLoadError(
                    f"Constitution file does not exist: {self.constitution_path}"
                )
            
            # Read YAML file / 读取YAML文件
            with open(self.constitution_path, "r", encoding="utf-8") as f:
                raw_data = yaml.safe_load(f)
            
            if not raw_data:
                raise ConstitutionLoadError("Constitution file is empty / 宪法文件为空")
            
            # Extract constitution part / 提取宪法部分
            if "constitution" not in raw_data:
                raise ConstitutionLoadError("Constitution file missing 'constitution' root key / 宪法文件缺少'constitution'根键")
            
            constitution_data = raw_data["constitution"]
            
            # Convert to Constitution object / 转换为Constitution对象
            try:
                self._constitution = Constitution(**constitution_data)
                logger.info("Constitution loaded successfully / 宪法加载成功")
                return self._constitution
            except Exception as e:
                raise ConstitutionLoadError(f"Constitution data validation failed: {str(e)}") from e
                
        except yaml.YAMLError as e:
            raise ConstitutionLoadError(f"YAML parsing failed: {str(e)}") from e
        except Exception as e:
            if isinstance(e, ConstitutionLoadError):
                raise
            raise ConstitutionLoadError(f"Unknown error occurred while loading constitution: {str(e)}") from e

    def reload(self) -> Constitution:
        """
        Reload Constitution Configuration / 重新加载宪法配置
        
        Returns:
            Constitution: Constitution object
        """
        logger.info("Reloading constitution configuration / 重新加载宪法配置")
        return self.load()

    @property
    def constitution(self) -> Constitution:
        """
        Get currently loaded constitution object / 获取当前加载的宪法对象
        
        Returns:
            Constitution: Constitution object
            
        Raises:
            ConstitutionLoadError: If constitution is not loaded
        """
        if self._constitution is None:
            raise ConstitutionLoadError("Constitution not loaded, please call load() method first / 宪法尚未加载，请先调用 load() 方法")
        return self._constitution

    def get_risk_limits(self) -> dict:
        """
        Get risk limit parameters / 获取风险限制参数
        
        Returns:
            dict: Risk limit parameters dictionary
        """
        return self.constitution.get_risk_limits()

    def get_market_state_parameters(self, state: str) -> Optional[dict]:
        """
        Get parameters for specific market state / 获取特定市场状态的参数
        
        Args:
            state: Market state name
            
        Returns:
            dict: Market state parameters, None if state does not exist
        """
        params = self.constitution.get_market_state_parameters(state)
        return params.model_dump() if params else None

    def get_emergency_triggers(self) -> list:
        """
        Get emergency triggers list / 获取紧急触发器列表
        
        Returns:
            list: Emergency triggers list
        """
        return self.constitution.get_emergency_triggers()
