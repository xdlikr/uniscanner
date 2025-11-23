"""
Constitution Validator
宪法验证器

Responsible for validating the integrity and business logic correctness of the constitution configuration.
负责验证宪法配置的完整性和业务逻辑正确性。
"""

import logging
from typing import List, Optional
from .schema import Constitution, MarketStateParameters

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Validation Error / 验证错误"""
    pass


class ConstitutionValidator:
    """Constitution Validator / 宪法验证器"""

    def __init__(self, constitution: Constitution):
        """
        Initialize Validator / 初始化验证器
        
        Args:
            constitution: Constitution object to validate
        """
        self.constitution = constitution
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self, strict: bool = True) -> bool:
        """
        Execute Full Validation / 执行完整验证
        
        Args:
            strict: Strict mode (warnings count as failure)
            
        Returns:
            bool: Whether validation passed
            
        Raises:
            ValidationError: If validation fails and strict=True
        """
        self.errors.clear()
        self.warnings.clear()
        
        logger.info("Start validating constitution configuration / 开始验证宪法配置")
        
        # Execute validations / 执行各项验证
        self._validate_risk_budget()
        self._validate_market_states()
        self._validate_emergency_rules()
        self._validate_execution_discipline()
        self._validate_business_logic()
        
        # Summarize results / 汇总结果
        has_errors = len(self.errors) > 0
        has_warnings = len(self.warnings) > 0
        
        if has_errors:
            error_msg = f"Constitution validation failed, found {len(self.errors)} errors / 宪法验证失败，发现 {len(self.errors)} 个错误"
            logger.error(error_msg)
            for error in self.errors:
                logger.error(f"  - {error}")
            if strict:
                raise ValidationError(f"{error_msg}: {'; '.join(self.errors)}")
            return False
        
        if has_warnings:
            logger.warning(f"Constitution validation passed with {len(self.warnings)} warnings / 宪法验证通过，但有 {len(self.warnings)} 个警告")
            for warning in self.warnings:
                logger.warning(f"  - {warning}")
            if strict:
                return False
        
        logger.info("Constitution validation passed / 宪法验证通过")
        return True

    def _validate_risk_budget(self) -> None:
        """Validate Risk Budget Configuration / 验证风险预算配置"""
        risk = self.constitution.risk_budget
        
        # Validate ratios / 验证比例关系
        if risk.max_single_position > risk.max_capital_usage:
            self.errors.append(
                f"Max single position ({risk.max_single_position}) cannot exceed max capital usage ({risk.max_capital_usage})"
            )
        
        if risk.max_sector_exposure > risk.max_capital_usage:
            self.errors.append(
                f"Max sector exposure ({risk.max_sector_exposure}) cannot exceed max capital usage ({risk.max_capital_usage})"
            )
        
        # Validate reasonableness / 验证合理性
        if risk.max_single_position > 0.25:
            self.warnings.append(
                f"Max single position too high ({risk.max_single_position}), suggest not exceeding 25%"
            )
        
        if risk.max_drawdown < 0.1:
            self.warnings.append(
                f"Max drawdown limit too strict ({risk.max_drawdown}), may cause excessive stop-loss"
            )
        
        if risk.max_drawdown > 0.3:
            self.warnings.append(
                f"Max drawdown limit too loose ({risk.max_drawdown}), high risk"
            )

    def _validate_market_states(self) -> None:
        """Validate Market States Configuration / 验证市场状态配置"""
        market_state = self.constitution.market_state
        
        # Check if all three standard states exist / 检查三个标准状态是否都存在
        required_states = ["normal_market", "cautious_market", "dangerous_market"]
        for state in required_states:
            if state not in market_state.parameters:
                self.errors.append(f"Missing market state parameters: {state}")
            if state not in market_state.definitions:
                self.errors.append(f"Missing market state definition: {state}")
        
        # Validate progressive relationship of parameters / 验证市场状态参数的递进关系
        if all(state in market_state.parameters for state in required_states):
            normal = market_state.parameters["normal_market"]
            cautious = market_state.parameters["cautious_market"]
            dangerous = market_state.parameters["dangerous_market"]
            
            # Max capital usage should decrease / 最大资金使用比率应该递减
            if not (dangerous.max_capital_usage <= cautious.max_capital_usage <= normal.max_capital_usage):
                self.errors.append(
                    "Market state max capital usage should decrease (Normal >= Cautious >= Dangerous)"
                )
            
            # Max single position should decrease / 单一头寸上限应该递减
            if not (dangerous.max_single_position <= cautious.max_single_position <= normal.max_single_position):
                self.errors.append(
                    "Market state max single position should decrease (Normal >= Cautious >= Dangerous)"
                )
            
            # Check min cash ratio / 检查现金比例下限
            if cautious.min_cash_ratio and normal.max_capital_usage > (1.0 - cautious.min_cash_ratio):
                self.warnings.append(
                    f"Cautious market min cash ratio ({cautious.min_cash_ratio}) may conflict with normal market max capital usage"
                )

    def _validate_emergency_rules(self) -> None:
        """Validate Emergency Rules Configuration / 验证紧急规则配置"""
        emergency = self.constitution.emergency_rules
        
        # Validate triggers / 验证触发器配置
        if not emergency.triggers:
            self.errors.append("Emergency rules missing triggers")
        
        # Validate response plan / 验证应对预案
        if not emergency.response_plan:
            self.errors.append("Emergency rules missing response plan")
        
        # Check if response plan has stages / 检查应对预案是否有阶段性
        if len(emergency.response_plan) < 2:
            self.warnings.append("Response plan suggests multiple stages (Warning/Crisis/Extreme)")

    def _validate_execution_discipline(self) -> None:
        """Validate Execution Discipline Configuration / 验证执行纪律配置"""
        execution = self.constitution.execution_discipline
        
        # Check best practices / 检查必要的最佳实践
        if not execution.best_practices:
            self.warnings.append("Execution discipline missing best practices")
        
        # Check price protection / 检查价格保护配置
        if not execution.price_protection:
            self.warnings.append("Suggest configuring price protection rules")

    def _validate_business_logic(self) -> None:
        """Validate Business Logic Consistency / 验证业务逻辑一致性"""
        
        # Check quality standards / 检查企业质量标准
        quality = self.constitution.quality_standards
        if not quality.business_model:
            self.errors.append("Quality standards missing business model assessment")
        if not quality.financial_health:
            self.errors.append("Quality standards missing financial health assessment")
        if not quality.management:
            self.errors.append("Quality standards missing management assessment")
        
        # Check valuation principles / 检查估值原则
        valuation = self.constitution.valuation_principles
        if not valuation.safety_margin:
            self.errors.append("Valuation principles missing safety margin configuration")
        if not valuation.methods:
            self.errors.append("Valuation principles missing valuation methods")
        
        # Check investment checklist / 检查投资检查清单
        checklist = self.constitution.investment_checklist
        if not checklist.before_buying:
            self.errors.append("Investment checklist missing pre-buy questions")
        if not checklist.during_holding:
            self.errors.append("Investment checklist missing holding monitoring questions")
        
        # Check LLM guidelines / 检查LLM使用规范
        llm = self.constitution.llm_guidelines
        if not llm.usage_scope:
            self.warnings.append("Suggest defining LLM usage scope")
        if not llm.restrictions:
            self.warnings.append("Suggest setting LLM restrictions")

    def get_validation_report(self) -> dict:
        """
        Get Validation Report / 获取验证报告
        
        Returns:
            dict: Report containing errors and warnings
        """
        return {
            "valid": len(self.errors) == 0,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors.copy(),
            "warnings": self.warnings.copy(),
        }
