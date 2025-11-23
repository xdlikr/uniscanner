"""
Test Constitution Validator
测试宪法验证器
"""

import pytest
from src.constitution.loader import ConstitutionLoader
from src.constitution.validator import ConstitutionValidator, ValidationError


class TestConstitutionValidator:
    """Constitution Validator Test / 宪法验证器测试"""

    def test_validate_valid_constitution(self, valid_constitution_path):
        """Test validating valid constitution / 测试验证有效的宪法"""
        loader = ConstitutionLoader(valid_constitution_path)
        constitution = loader.load()
        
        validator = ConstitutionValidator(constitution)
        result = validator.validate(strict=False)
        
        assert result is True

    def test_validate_invalid_constitution(self, invalid_constitution_path):
        """Test validating invalid constitution / 测试验证无效的宪法"""
        loader = ConstitutionLoader(invalid_constitution_path)
        
        # Loading fails because data is out of range / 加载会失败因为数据超出范围
        with pytest.raises(Exception):
            constitution = loader.load()

    def test_validation_report(self, valid_constitution_path):
        """Test getting validation report / 测试获取验证报告"""
        loader = ConstitutionLoader(valid_constitution_path)
        constitution = loader.load()
        
        validator = ConstitutionValidator(constitution)
        validator.validate(strict=False)
        
        report = validator.get_validation_report()
        
        assert "valid" in report
        assert "error_count" in report
        assert "warning_count" in report
        assert "errors" in report
        assert "warnings" in report
        assert isinstance(report["errors"], list)
        assert isinstance(report["warnings"], list)

    def test_risk_budget_validation(self, valid_constitution_path):
        """Test risk budget validation / 测试风险预算验证"""
        loader = ConstitutionLoader(valid_constitution_path)
        constitution = loader.load()
        
        validator = ConstitutionValidator(constitution)
        validator._validate_risk_budget()
        
        # Valid config should have no errors / 有效配置不应有错误
        assert len(validator.errors) == 0

    def test_market_states_validation(self, valid_constitution_path):
        """Test market states validation / 测试市场状态验证"""
        loader = ConstitutionLoader(valid_constitution_path)
        constitution = loader.load()
        
        validator = ConstitutionValidator(constitution)
        validator._validate_market_states()
        
        # Check for market state errors / 检查是否有市场状态相关的错误
        # Valid config might have warnings but no errors / 有效配置可能有警告但不应有严重错误
        assert all("normal_market" not in error for error in validator.errors) or len(validator.errors) == 0

    def test_emergency_rules_validation(self, valid_constitution_path):
        """Test emergency rules validation / 测试紧急规则验证"""
        loader = ConstitutionLoader(valid_constitution_path)
        constitution = loader.load()
        
        validator = ConstitutionValidator(constitution)
        validator._validate_emergency_rules()
        
        # Valid config should have emergency rules / 有效配置应该有紧急规则
        assert len(validator.errors) == 0

    def test_strict_mode_validation(self, valid_constitution_path):
        """Test strict mode validation / 测试严格模式验证"""
        loader = ConstitutionLoader(valid_constitution_path)
        constitution = loader.load()
        
        validator = ConstitutionValidator(constitution)
        
        # Non-strict mode: pass with warnings / 非严格模式：有警告也通过
        result = validator.validate(strict=False)
        
        # Decide based on warning count / 根据警告数量决定是否通过
        if validator.warnings:
            # If warnings exist, should fail in strict mode / 如果有警告，在严格模式下应该失败
            result_strict = validator.validate(strict=True)
            assert result_strict is False
        else:
            assert result is True
