"""
Test Constitution Loader
测试宪法加载器
"""

import pytest
from pathlib import Path
from src.constitution.loader import ConstitutionLoader, ConstitutionLoadError
from src.constitution.schema import Constitution


class TestConstitutionLoader:
    """Constitution Loader Test / 宪法加载器测试"""

    def test_load_valid_constitution(self, valid_constitution_path):
        """Test loading valid constitution / 测试加载有效的宪法文件"""
        loader = ConstitutionLoader(valid_constitution_path)
        constitution = loader.load()
        
        assert isinstance(constitution, Constitution)
        assert constitution.meta_info.title == "Test Constitution"
        assert len(constitution.core_principles) > 0

    def test_load_nonexistent_file(self):
        """Test loading nonexistent file / 测试加载不存在的文件"""
        loader = ConstitutionLoader(Path("nonexistent.yaml"))
        
        with pytest.raises(ConstitutionLoadError) as exc_info:
            loader.load()
        
        assert "does not exist" in str(exc_info.value)

    def test_get_risk_limits(self, valid_constitution_path):
        """Test getting risk limits / 测试获取风险限制"""
        loader = ConstitutionLoader(valid_constitution_path)
        loader.load()
        
        risk_limits = loader.get_risk_limits()
        
        assert "max_capital_usage" in risk_limits
        assert "max_single_position" in risk_limits
        assert "max_sector_exposure" in risk_limits
        assert "max_drawdown" in risk_limits
        assert 0 <= risk_limits["max_capital_usage"] <= 1
        assert 0 <= risk_limits["max_drawdown"] <= 1

    def test_get_market_state_parameters(self, valid_constitution_path):
        """Test getting market state parameters / 测试获取市场状态参数"""
        loader = ConstitutionLoader(valid_constitution_path)
        loader.load()
        
        normal_params = loader.get_market_state_parameters("normal_market")
        assert normal_params is not None
        assert "max_capital_usage" in normal_params
        assert normal_params["max_capital_usage"] == 0.90
        
        invalid_params = loader.get_market_state_parameters("nonexistent_state")
        assert invalid_params is None

    def test_get_emergency_triggers(self, valid_constitution_path):
        """Test getting emergency triggers / 测试获取紧急触发器"""
        loader = ConstitutionLoader(valid_constitution_path)
        loader.load()
        
        triggers = loader.get_emergency_triggers()
        assert isinstance(triggers, list)
        assert len(triggers) > 0
        # assert "description" in triggers[0] # Triggers are now just strings in the new schema

    def test_constitution_property_before_load(self):
        """Test accessing constitution property before load / 测试在加载前访问constitution属性"""
        loader = ConstitutionLoader(Path("dummy.yaml"))
        
        with pytest.raises(ConstitutionLoadError) as exc_info:
            _ = loader.constitution
        
        assert "not loaded" in str(exc_info.value)

    def test_reload(self, valid_constitution_path):
        """Test reload / 测试重新加载"""
        loader = ConstitutionLoader(valid_constitution_path)
        constitution1 = loader.load()
        constitution2 = loader.reload()
        
        assert isinstance(constitution2, Constitution)
        assert constitution1.meta_info.title == constitution2.meta_info.title
