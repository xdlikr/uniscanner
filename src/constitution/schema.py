"""
Constitution Data Structure Definition
宪法数据结构定义

Define all data structures in the constitution using Pydantic to ensure type safety and data validation.
使用 Pydantic 定义宪法中的所有数据结构，确保类型安全和数据验证。
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


class SystemMode(str, Enum):
    """System Operation Mode / 系统运行模式"""
    SIMULATION = "SIMULATION"
    DRY_RUN = "DRY_RUN"
    LIVE = "LIVE"
    EMERGENCY = "EMERGENCY"


class MarketStateType(str, Enum):
    """Market State Type / 市场状态类型"""
    NORMAL = "normal_market" # 正常市场
    CAUTIOUS = "cautious_market" # 谨慎市场
    DANGEROUS = "dangerous_market" # 危险市场


class SystemIdentity(BaseModel):
    """System Identity Declaration / 系统身份声明"""
    system_type: str = Field(description="System Type / 系统类型")
    operation_frequency: str = Field(description="Operation Frequency / 操作频率")
    inspirations: List[str] = Field(description="Inspirations / 灵感来源")
    
    model_config = ConfigDict(populate_by_name=True)


class MarketStateParameters(BaseModel):
    """Risk Parameters under Market State / 市场状态下的风险参数"""
    max_capital_usage: float = Field(ge=0.0, le=1.0, description="Max Capital Usage Ratio / 最大资金使用比率")
    max_single_position: float = Field(ge=0.0, le=1.0, description="Max Single Position Limit / 单一头寸上限")
    safety_margin_requirement: str = Field(description="New Position Safety Margin Requirement / 新建仓安全边际要求")
    min_cash_ratio: Optional[float] = Field(None, ge=0.0, le=1.0, description="Min Cash Ratio / 现金比例下限")
    allow_adding_position: Optional[bool] = Field(None, description="Allow Adding to Existing Positions / 是否允许对现有持仓加仓")
    
    model_config = ConfigDict(populate_by_name=True)


class MarketState(BaseModel):
    """Market State Perception / 市场状态感知"""
    identifiers: List[str] = Field(description="Market State Identifiers / 市场状态识别因子")
    definitions: Dict[str, str] = Field(description="State Definitions / 市场状态定义")
    parameters: Dict[str, MarketStateParameters] = Field(description="Parameters for Different Market States / 不同市场状态的参数")
    
    model_config = ConfigDict(populate_by_name=True)


class RiskBudget(BaseModel):
    """Risk Budget Configuration / 风险预算配置"""
    max_capital_usage: float = Field(ge=0.0, le=1.0, description="Max Capital Usage Ratio / 最大资金使用比率")
    max_single_position: float = Field(ge=0.0, le=1.0, description="Max Single Position Limit / 单一头寸上限")
    max_sector_exposure: float = Field(ge=0.0, le=1.0, description="Max Sector Exposure Limit / 单一行业暴露上限")
    max_drawdown: float = Field(ge=0.0, le=1.0, description="Max Drawdown Limit / 最大回撤限制")
    liquidity_requirements: Dict[str, Any] = Field(description="Liquidity Requirements / 流动性要求")
    
    model_config = ConfigDict(populate_by_name=True)


class QualityStandards(BaseModel):
    """Business Quality Standards / 企业质量标准"""
    business_model: List[str] = Field(description="Business Model Assessment Standards / 商业模式评估标准")
    financial_health: List[str] = Field(description="Financial Health Assessment Standards / 财务健康评估标准")
    management: List[str] = Field(description="Management Assessment Standards / 管理层评估标准")
    
    model_config = ConfigDict(populate_by_name=True)


class SafetyMargin(BaseModel):
    """Safety Margin Configuration / 安全边际配置"""
    normal: str = Field(description="Normal Valuation Requirement / 正常估值要求")
    preferred: str = Field(description="Preferred Valuation Requirement / 优选估值要求")
    excellent: str = Field(description="Excellent Valuation Requirement / 极佳估值要求")
    
    model_config = ConfigDict(populate_by_name=True)


class ValuationPrinciples(BaseModel):
    """Valuation Principles / 估值原则"""
    safety_margin: SafetyMargin = Field(description="Safety Margin Configuration / 安全边际配置")
    methods: List[str] = Field(description="Valuation Methods / 估值方法")
    
    model_config = ConfigDict(populate_by_name=True)


class EmergencyRules(BaseModel):
    """Emergency Rules Configuration / 紧急规则配置"""
    triggers: List[str] = Field(description="Triggers List / 触发器列表")
    response_plan: Dict[str, str] = Field(description="Response Plan / 应对预案")
    cooldown_rules: List[str] = Field(description="Cooldown Rules / 冷静期规则")
    
    model_config = ConfigDict(populate_by_name=True)


class ExecutionDiscipline(BaseModel):
    """Execution Discipline / 执行纪律"""
    best_practices: List[str] = Field(description="Trading Best Practices / 交易最佳实践")
    price_protection: List[str] = Field(description="Price Protection Configuration / 价格保护配置")
    
    model_config = ConfigDict(populate_by_name=True)


class LLMGuidelines(BaseModel):
    """LLM Guidelines / LLM辅助规范"""
    role: str = Field(description="Role Definition / 角色定位")
    usage_scope: List[str] = Field(description="Allowed Usage Scope / 允许使用的范围")
    restrictions: List[str] = Field(description="Restrictions / 限制规则")
    
    model_config = ConfigDict(populate_by_name=True)


class StressTestRequirements(BaseModel):
    """Stress Test Requirements / 压力测试要求"""
    historical_scenarios: List[str] = Field(description="Mandatory Historical Scenarios / 必须测试的历史场景")
    passing_criteria: List[str] = Field(description="Passing Criteria / 通过标准")
    
    model_config = ConfigDict(populate_by_name=True)


class InvestmentChecklist(BaseModel):
    """Investment Checklist / 投资检查清单"""
    before_buying: List[str] = Field(description="Questions Before Buying / 买入前必须回答的问题")
    during_holding: List[str] = Field(description="Monitoring During Holding / 持有期间监控的问题")
    
    model_config = ConfigDict(populate_by_name=True)


class MetaInfo(BaseModel):
    """Constitution Meta Info / 宪法元信息"""
    title: str = Field(description="Constitution Title / 宪法标题")
    core_concept: str = Field(description="Core Concept / 核心理念")
    philosophy: str = Field(description="Investment Philosophy / 投资哲学")
    risk_first: str = Field(description="Risk First Principle / 风险第一原则")
    
    model_config = ConfigDict(populate_by_name=True)


class Constitution(BaseModel):
    """Constitution Main Data Structure / 宪法主数据结构"""
    meta_info: MetaInfo = Field(alias="meta_info") # 元信息
    system_identity: SystemIdentity = Field(alias="system_identity") # 身份声明
    core_principles: List[str] = Field(alias="core_principles") # 核心投资原则
    market_state: MarketState = Field(alias="market_state") # 市场状态感知
    risk_budget: RiskBudget = Field(alias="risk_budget") # 风险预算
    quality_standards: QualityStandards = Field(alias="quality_standards") # 企业质量标准
    valuation_principles: ValuationPrinciples = Field(alias="valuation_principles") # 估值原则
    emergency_rules: EmergencyRules = Field(alias="emergency_rules") # 紧急规则
    execution_discipline: ExecutionDiscipline = Field(alias="execution_discipline") # 执行纪律
    llm_guidelines: LLMGuidelines = Field(alias="llm_guidelines") # LLM辅助规范
    stress_test_requirements: StressTestRequirements = Field(alias="stress_test_requirements") # 压力测试要求
    investment_checklist: InvestmentChecklist = Field(alias="investment_checklist") # 投资检查清单
    cash_management_philosophy: List[str] = Field(alias="cash_management_philosophy") # 现金管理哲学
    final_principles: List[str] = Field(alias="final_principles") # 最终原则
    
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("core_principles", "cash_management_philosophy", "final_principles")
    @classmethod
    def validate_non_empty_list(cls, v: List[str]) -> List[str]:
        """Validate list is not empty / 验证列表不为空"""
        if not v:
            raise ValueError("List cannot be empty / 列表不能为空")
        return v

    def get_risk_limits(self) -> Dict[str, float]:
        """Get Risk Limit Parameters / 获取风险限制参数"""
        return {
            "max_capital_usage": self.risk_budget.max_capital_usage,
            "max_single_position": self.risk_budget.max_single_position,
            "max_sector_exposure": self.risk_budget.max_sector_exposure,
            "max_drawdown": self.risk_budget.max_drawdown,
        }

    def get_market_state_parameters(self, state: str) -> Optional[MarketStateParameters]:
        """Get Parameters for Specific Market State / 获取特定市场状态的参数"""
        return self.market_state.parameters.get(state)

    def get_emergency_triggers(self) -> List[str]:
        """Get Emergency Triggers List / 获取紧急触发器列表"""
        return self.emergency_rules.triggers
