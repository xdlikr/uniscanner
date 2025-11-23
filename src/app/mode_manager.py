"""
Mode Manager
模式管理器

Manage the state machine of system operation modes, ensuring safety and traceability of mode transitions.
管理系统运行模式的状态机，确保模式切换的安全性和可追溯性。
"""

import logging
from enum import Enum
from typing import Optional
from datetime import datetime, timezone

from .logging_setup import AuditLogger, AuditEventType

logger = logging.getLogger(__name__)


class SystemMode(str, Enum):
    """System Operation Mode / 系统运行模式"""
    SIMULATION = "SIMULATION"
    DRY_RUN = "DRY_RUN"
    LIVE = "LIVE"
    EMERGENCY = "EMERGENCY"


class ModeTransitionError(Exception):
    """Mode Transition Error / 模式切换错误"""
    pass


class ModeManager:
    """Mode Manager - Implements 3-state (+Emergency) State Machine / 模式管理器 - 实现三态（+紧急态）状态机"""

    # Define allowed transitions / 定义允许的状态转换
    ALLOWED_TRANSITIONS = {
        SystemMode.SIMULATION: [SystemMode.DRY_RUN],
        SystemMode.DRY_RUN: [SystemMode.SIMULATION, SystemMode.LIVE, SystemMode.EMERGENCY],
        SystemMode.LIVE: [SystemMode.DRY_RUN, SystemMode.EMERGENCY],
        SystemMode.EMERGENCY: [SystemMode.DRY_RUN],
    }

    def __init__(
        self,
        initial_mode: SystemMode = SystemMode.SIMULATION,
        audit_logger: Optional[AuditLogger] = None,
        require_confirmation_for_live: bool = True,
    ):
        """
        Initialize Mode Manager / 初始化模式管理器
        
        Args:
            initial_mode: Initial mode
            audit_logger: Audit logger
            require_confirmation_for_live: Whether switching to LIVE mode requires manual confirmation
        """
        self._current_mode = initial_mode
        self._previous_mode: Optional[SystemMode] = None
        self._mode_history: list = []
        self._audit_logger = audit_logger
        self._require_confirmation_for_live = require_confirmation_for_live
        
        # Record initial mode / 记录初始模式
        self._record_mode_change(None, initial_mode, "System Initialization / 系统初始化")
        logger.info(f"Mode manager initialized, current mode: {initial_mode.value}")

    @property
    def current_mode(self) -> SystemMode:
        """Get current mode / 获取当前模式"""
        return self._current_mode

    @property
    def previous_mode(self) -> Optional[SystemMode]:
        """Get previous mode / 获取上一个模式"""
        return self._previous_mode

    def is_simulation(self) -> bool:
        """Is simulation mode / 是否为仿真模式"""
        return self._current_mode == SystemMode.SIMULATION

    def is_dry_run(self) -> bool:
        """Is dry run mode / 是否为影子模式"""
        return self._current_mode == SystemMode.DRY_RUN

    def is_live(self) -> bool:
        """Is live mode / 是否为实盘模式"""
        return self._current_mode == SystemMode.LIVE

    def is_emergency(self) -> bool:
        """Is emergency mode / 是否为紧急模式"""
        return self._current_mode == SystemMode.EMERGENCY

    def can_trade(self) -> bool:
        """
        Check if real trading is allowed in current mode
        判断当前模式是否允许真实交易
        
        Returns:
            bool: Whether real trading is allowed
        """
        return self._current_mode == SystemMode.LIVE

    def can_analyze(self) -> bool:
        """
        Check if analysis is allowed in current mode
        判断当前模式是否允许分析
        
        Returns:
            bool: Whether analysis is allowed (allowed in all except EMERGENCY)
        """
        return self._current_mode != SystemMode.EMERGENCY

    def switch_mode(
        self,
        target_mode: SystemMode,
        reason: str = "",
        user: Optional[str] = None,
        force: bool = False,
    ) -> bool:
        """
        Switch System Mode / 切换系统模式
        
        Args:
            target_mode: Target mode
            reason: Reason for switch
            user: Operating user
            force: Whether to force switch (skip transition rule check)
            
        Returns:
            bool: Whether switch was successful
            
        Raises:
            ModeTransitionError: If switch is not allowed
        """
        if target_mode == self._current_mode:
            logger.info(f"Target mode is same as current mode, no switch needed: {target_mode.value}")
            return True

        # Check if transition is allowed / 检查转换是否被允许
        if not force and target_mode not in self.ALLOWED_TRANSITIONS[self._current_mode]:
            error_msg = (
                f"Transition from {self._current_mode.value} to {target_mode.value} is not allowed. "
                f"Allowed transitions: {[m.value for m in self.ALLOWED_TRANSITIONS[self._current_mode]]}"
            )
            logger.error(error_msg)
            
            # Record denied switch attempt / 记录拒绝的切换尝试
            if self._audit_logger:
                self._audit_logger.log_event(
                    AuditEventType.MODE_SWITCH_DENIED,
                    error_msg,
                    details={
                        "current_mode": self._current_mode.value,
                        "target_mode": target_mode.value,
                        "reason": reason,
                    },
                    user=user,
                )
            
            raise ModeTransitionError(error_msg)

        # LIVE mode requires manual confirmation / LIVE模式需要人工确认
        if target_mode == SystemMode.LIVE and self._require_confirmation_for_live and not force:
            confirmation_msg = (
                f"⚠️  WARNING: About to switch to LIVE mode! / 警告: 即将切换到实盘模式 (LIVE)！\n"
                f"Current mode: {self._current_mode.value}\n"
                f"Reason: {reason or 'Not provided'}\n"
                f"Please use force=True to explicitly confirm this operation."
            )
            logger.warning(confirmation_msg)
            raise ModeTransitionError("Switching to LIVE mode requires explicit confirmation (force=True)")

        # Execute switch / 执行切换
        old_mode = self._current_mode
        self._previous_mode = old_mode
        self._current_mode = target_mode
        
        # Record switch / 记录切换
        self._record_mode_change(old_mode, target_mode, reason, user)
        
        logger.info(
            f"Mode switch successful: {old_mode.value} -> {target_mode.value} "
            f"(Reason: {reason or 'Not provided'})"
        )
        
        return True

    def trigger_emergency(
        self,
        reason: str,
        user: Optional[str] = None,
    ) -> bool:
        """
        Trigger Emergency Mode / 触发紧急模式
        
        Args:
            reason: Reason for trigger
            user: Operating user
            
        Returns:
            bool: Whether switch was successful
        """
        logger.critical(f"🚨 Emergency Mode Triggered! Reason: {reason}")
        
        # Emergency mode can be triggered from any state / 紧急模式可以从任何状态触发
        old_mode = self._current_mode
        self._previous_mode = old_mode
        self._current_mode = SystemMode.EMERGENCY
        
        # Record emergency trigger / 记录紧急触发
        if self._audit_logger:
            self._audit_logger.log_event(
                AuditEventType.EMERGENCY_TRIGGERED,
                f"Emergency mode triggered: {reason}",
                details={
                    "previous_mode": old_mode.value,
                    "reason": reason,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                user=user,
            )
        
        self._record_mode_change(old_mode, SystemMode.EMERGENCY, f"Emergency Trigger: {reason}", user)
        
        return True

    def _record_mode_change(
        self,
        old_mode: Optional[SystemMode],
        new_mode: SystemMode,
        reason: str,
        user: Optional[str] = None,
    ) -> None:
        """
        Record Mode Change / 记录模式变更
        
        Args:
            old_mode: Old mode
            new_mode: New mode
            reason: Change reason
            user: Operating user
        """
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "old_mode": old_mode.value if old_mode else None,
            "new_mode": new_mode.value,
            "reason": reason,
            "user": user,
        }
        
        self._mode_history.append(record)
        
        # Audit log / 审计日志
        if self._audit_logger:
            self._audit_logger.log_event(
                AuditEventType.MODE_SWITCHED,
                f"Mode Switched: {old_mode.value if old_mode else 'None'} -> {new_mode.value}",
                details=record,
                user=user,
            )

    def get_mode_history(self) -> list:
        """
        Get Mode Change History / 获取模式变更历史
        
        Returns:
            list: List of mode change records
        """
        return self._mode_history.copy()

    def get_mode_description(self, mode: Optional[SystemMode] = None) -> str:
        """
        Get Mode Description / 获取模式描述
        
        Args:
            mode: Mode to describe, None for current mode
            
        Returns:
            str: Mode description
        """
        target_mode = mode or self._current_mode
        
        descriptions = {
            SystemMode.SIMULATION: "Simulation Mode - Replay/Backtest, No Broker Connection / 仿真模式 - 回放/回测，不连券商",
            SystemMode.DRY_RUN: "Dry Run Mode - Connected to Market, No Real Orders / 影子模式 - 连行情，不下真实单",
            SystemMode.LIVE: "Live Mode - Automated Trading / 实盘模式 - 自动交易",
            SystemMode.EMERGENCY: "Emergency Mode - Only Reduce/Clear Positions, No New Positions / 紧急模式 - 只允许减仓或清仓，禁止新增仓位",
        }
        
        return descriptions.get(target_mode, "Unknown Mode / 未知模式")

    def __str__(self) -> str:
        """String representation"""
        return f"ModeManager(current={self._current_mode.value})"

    def __repr__(self) -> str:
        """Detailed representation"""
        return (
            f"ModeManager(current={self._current_mode.value}, "
            f"previous={self._previous_mode.value if self._previous_mode else None})"
        )
