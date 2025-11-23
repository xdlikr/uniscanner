"""
Test Mode Manager
测试模式管理器
"""

import pytest
from src.app.mode_manager import ModeManager, SystemMode, ModeTransitionError
from src.app.logging_setup import setup_logging


class TestModeManager:
    """Mode Manager Test / 模式管理器测试"""

    def test_initial_mode(self):
        """Test initial mode / 测试初始模式"""
        manager = ModeManager(initial_mode=SystemMode.SIMULATION)
        assert manager.current_mode == SystemMode.SIMULATION
        assert manager.is_simulation()

    def test_allowed_transition(self, temp_log_dir):
        """Test allowed transition / 测试允许的状态转换"""
        audit_logger = setup_logging(log_dir=temp_log_dir, enable_console=False)
        manager = ModeManager(
            initial_mode=SystemMode.SIMULATION,
            audit_logger=audit_logger,
            require_confirmation_for_live=False
        )
        
        # SIMULATION -> DRY_RUN (Allowed)
        result = manager.switch_mode(SystemMode.DRY_RUN, "Test Switch")
        assert result is True
        assert manager.current_mode == SystemMode.DRY_RUN
        assert manager.is_dry_run()

    def test_disallowed_transition(self):
        """Test disallowed transition / 测试不允许的状态转换"""
        manager = ModeManager(initial_mode=SystemMode.SIMULATION)
        
        # SIMULATION -> LIVE (Not allowed, must go through DRY_RUN)
        with pytest.raises(ModeTransitionError) as exc_info:
            manager.switch_mode(SystemMode.LIVE, "Illegal Switch")
        
        assert "not allowed" in str(exc_info.value)

    def test_live_mode_confirmation(self):
        """Test LIVE mode confirmation / 测试LIVE模式需要确认"""
        manager = ModeManager(
            initial_mode=SystemMode.DRY_RUN,
            require_confirmation_for_live=True
        )
        
        # Not confirmed, should raise exception / 未确认，应该抛出异常
        with pytest.raises(ModeTransitionError) as exc_info:
            manager.switch_mode(SystemMode.LIVE, "Switch to Live")
        
        assert "requires explicit confirmation" in str(exc_info.value)
        
        # Confirm with force=True / 使用force=True确认
        result = manager.switch_mode(SystemMode.LIVE, "Switch to Live", force=True)
        assert result is True
        assert manager.is_live()

    def test_emergency_trigger(self, temp_log_dir):
        """Test emergency trigger / 测试紧急模式触发"""
        audit_logger = setup_logging(log_dir=temp_log_dir, enable_console=False)
        manager = ModeManager(
            initial_mode=SystemMode.LIVE,
            audit_logger=audit_logger
        )
        
        # Trigger emergency mode / 触发紧急模式
        result = manager.trigger_emergency("Market Anomaly")
        assert result is True
        assert manager.is_emergency()
        assert manager.previous_mode == SystemMode.LIVE

    def test_mode_history(self):
        """Test mode history / 测试模式历史记录"""
        manager = ModeManager(initial_mode=SystemMode.SIMULATION)
        
        # Should have one initial record / 初始应该有一条记录
        history = manager.get_mode_history()
        assert len(history) >= 1
        
        # Switch mode / 切换模式
        manager.switch_mode(SystemMode.DRY_RUN, "Test")
        history = manager.get_mode_history()
        assert len(history) >= 2
        
        # Check record content / 检查记录内容
        last_record = history[-1]
        assert last_record["old_mode"] == SystemMode.SIMULATION.value
        assert last_record["new_mode"] == SystemMode.DRY_RUN.value
        assert "timestamp" in last_record
        assert "reason" in last_record

    def test_can_trade(self):
        """Test can trade / 测试是否允许交易"""
        manager = ModeManager(initial_mode=SystemMode.SIMULATION)
        assert manager.can_trade() is False
        
        manager = ModeManager(initial_mode=SystemMode.DRY_RUN)
        assert manager.can_trade() is False
        
        manager = ModeManager(
            initial_mode=SystemMode.LIVE,
            require_confirmation_for_live=False
        )
        # Note: Initialize directly to LIVE requires disabling confirmation / 注意：直接初始化为LIVE需要关闭确认
        assert manager.current_mode == SystemMode.LIVE
        assert manager.can_trade() is True

    def test_can_analyze(self):
        """Test can analyze / 测试是否允许分析"""
        manager = ModeManager(initial_mode=SystemMode.SIMULATION)
        assert manager.can_analyze() is True
        
        manager = ModeManager(initial_mode=SystemMode.EMERGENCY)
        assert manager.can_analyze() is False

    def test_mode_description(self):
        """Test mode description / 测试模式描述"""
        manager = ModeManager(initial_mode=SystemMode.SIMULATION)
        
        desc = manager.get_mode_description()
        assert isinstance(desc, str)
        assert len(desc) > 0
        
        desc_dryrun = manager.get_mode_description(SystemMode.DRY_RUN)
        assert "Dry Run" in desc_dryrun

    def test_force_switch(self):
        """Test force switch / 测试强制切换"""
        manager = ModeManager(initial_mode=SystemMode.SIMULATION)
        
        # Force switch skips transition rules / 使用force跳过转换规则
        result = manager.switch_mode(SystemMode.LIVE, "Force Switch", force=True)
        assert result is True
        assert manager.is_live()

    def test_same_mode_switch(self):
        """Test same mode switch / 测试切换到相同模式"""
        manager = ModeManager(initial_mode=SystemMode.SIMULATION)
        
        # Switch to same mode should return True directly / 切换到相同模式应该直接返回True
        result = manager.switch_mode(SystemMode.SIMULATION, "Same Mode")
        assert result is True

    def test_string_representation(self):
        """Test string representation / 测试字符串表示"""
        manager = ModeManager(initial_mode=SystemMode.SIMULATION)
        
        str_repr = str(manager)
        assert "SIMULATION" in str_repr
        
        repr_str = repr(manager)
        assert "ModeManager" in repr_str
