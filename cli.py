#!/usr/bin/env python3
"""
Uniscanner CLI - Constitution Management and System Control Tool
Uniscanner CLI - 宪法管理和系统控制工具

Provides command line interface to manage constitution configuration and system modes.
提供命令行接口来管理宪法配置和系统模式。
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Add src to path / 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from colorama import init, Fore, Style

from src.constitution.loader import ConstitutionLoader, ConstitutionLoadError
from src.constitution.validator import ConstitutionValidator, ValidationError
from src.app.mode_manager import ModeManager, SystemMode, ModeTransitionError
from src.app.logging_setup import setup_logging
from src.config.loader import ConfigLoader

# Initialize colorama / 初始化colorama
init(autoreset=True)


class CLI:
    """CLI Controller / CLI控制器"""

    def __init__(self):
        """Initialize CLI / 初始化CLI"""
        self.config_loader = ConfigLoader()
        self.constitution_loader: Optional[ConstitutionLoader] = None
        self.mode_manager: Optional[ModeManager] = None

    def load_constitution(self, path: Optional[Path] = None) -> bool:
        """
        Load Constitution File / 加载宪法文件
        
        Args:
            path: Constitution file path
            
        Returns:
            bool: Success or not
        """
        try:
            print(f"{Fore.CYAN}Loading constitution file... / 正在加载宪法文件...{Style.RESET_ALL}")
            
            if path is None:
                path = Path("constitution.yaml")
            
            self.constitution_loader = ConstitutionLoader(path)
            constitution = self.constitution_loader.load()
            
            print(f"{Fore.GREEN}✓ Constitution loaded successfully / 宪法加载成功{Style.RESET_ALL}")
            print(f"  Title: {constitution.meta_info.title}")
            print(f"  Concept: {constitution.meta_info.core_concept}")
            print(f"  Path: {path}")
            
            return True
            
        except ConstitutionLoadError as e:
            print(f"{Fore.RED}✗ Constitution load failed: {e} / 宪法加载失败{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"{Fore.RED}✗ Unknown error occurred: {e} / 发生未知错误{Style.RESET_ALL}")
            return False

    def validate_constitution(self, strict: bool = False) -> bool:
        """
        Validate Constitution Configuration / 验证宪法配置
        
        Args:
            strict: Strict mode
            
        Returns:
            bool: Validation passed or not
        """
        if self.constitution_loader is None:
            print(f"{Fore.YELLOW}Please load constitution file first / 请先加载宪法文件{Style.RESET_ALL}")
            return False
        
        try:
            print(f"{Fore.CYAN}Validating constitution configuration... / 正在验证宪法配置...{Style.RESET_ALL}")
            
            constitution = self.constitution_loader.constitution
            validator = ConstitutionValidator(constitution)
            
            result = validator.validate(strict=strict)
            report = validator.get_validation_report()
            
            if result:
                print(f"{Fore.GREEN}✓ Constitution validation passed / 宪法验证通过{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✗ Constitution validation failed / 宪法验证失败{Style.RESET_ALL}")
            
            # Show errors / 显示错误
            if report["errors"]:
                print(f"\n{Fore.RED}Errors ({report['error_count']}): / 错误 ({report['error_count']}个):{Style.RESET_ALL}")
                for i, error in enumerate(report["errors"], 1):
                    print(f"  {i}. {error}")
            
            # Show warnings / 显示警告
            if report["warnings"]:
                print(f"\n{Fore.YELLOW}Warnings ({report['warning_count']}): / 警告 ({report['warning_count']}个):{Style.RESET_ALL}")
                for i, warning in enumerate(report["warnings"], 1):
                    print(f"  {i}. {warning}")
            
            return result
            
        except ValidationError as e:
            print(f"{Fore.RED}✗ Validation failed: {e} / 验证失败{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"{Fore.RED}✗ Unknown error occurred: {e} / 发生未知错误{Style.RESET_ALL}")
            return False

    def show_mode(self) -> None:
        """Show Current System Mode / 显示当前系统模式"""
        if self.mode_manager is None:
            # Read from config / 从配置读取
            try:
                config = self.config_loader.load()
                current_mode = config.system_mode
                print(f"{Fore.CYAN}Current System Mode: / 当前系统模式:{Style.RESET_ALL} {current_mode}")
                
                # Show mode description / 显示模式描述
                mode_enum = SystemMode(current_mode)
                manager = ModeManager(initial_mode=mode_enum)
                desc = manager.get_mode_description()
                print(f"  {desc}")
            except Exception as e:
                print(f"{Fore.RED}Failed to read system mode: {e} / 无法读取系统模式{Style.RESET_ALL}")
        else:
            mode = self.mode_manager.current_mode
            desc = self.mode_manager.get_mode_description()
            
            print(f"{Fore.CYAN}Current System Mode: / 当前系统模式:{Style.RESET_ALL} {mode.value}")
            print(f"  {desc}")
            
            if self.mode_manager.previous_mode:
                print(f"  Previous Mode: {self.mode_manager.previous_mode.value} / 上一个模式")

    def switch_mode(self, target_mode: str, reason: str = "", force: bool = False) -> bool:
        """
        Switch System Mode / 切换系统模式
        
        Args:
            target_mode: Target mode
            reason: Switch reason
            force: Force switch
            
        Returns:
            bool: Success or not
        """
        try:
            # Initialize mode_manager / 初始化mode_manager
            if self.mode_manager is None:
                config = self.config_loader.load()
                current_mode = SystemMode(config.system_mode)
                
                # Setup logging / 设置日志
                audit_logger = setup_logging(
                    log_level=config.log_level,
                    log_dir=config.log_dir,
                    enable_console=False
                )
                
                self.mode_manager = ModeManager(
                    initial_mode=current_mode,
                    audit_logger=audit_logger
                )
            
            target = SystemMode(target_mode)
            
            print(f"{Fore.CYAN}Switching mode... / 正在切换模式...{Style.RESET_ALL}")
            print(f"  From: {self.mode_manager.current_mode.value}")
            print(f"  To: {target.value}")
            if reason:
                print(f"  Reason: {reason}")
            
            # If LIVE mode and requires confirmation / 如果是LIVE模式且需要确认
            if target == SystemMode.LIVE and not force:
                print(f"\n{Fore.YELLOW}⚠️  WARNING: About to switch to LIVE mode! / 警告: 即将切换到实盘模式 (LIVE)！{Style.RESET_ALL}")
                print("This will allow the system to execute real trades. / 这将允许系统进行真实交易。")
                response = input("Confirm switch? (Type 'YES' to continue): / 是否确认切换？(输入 'YES' 继续): ")
                
                if response != "YES":
                    print(f"{Fore.YELLOW}Switch cancelled / 已取消切换{Style.RESET_ALL}")
                    return False
                
                force = True
            
            self.mode_manager.switch_mode(target, reason=reason, force=force)
            
            print(f"{Fore.GREEN}✓ Mode switch successful / 模式切换成功{Style.RESET_ALL}")
            print(f"  Current Mode: {self.mode_manager.current_mode.value}")
            
            return True
            
        except ValueError as e:
            print(f"{Fore.RED}✗ Invalid mode: {target_mode} / 无效的模式{Style.RESET_ALL}")
            print(f"  Available modes: SIMULATION, DRY_RUN, LIVE, EMERGENCY")
            return False
        except ModeTransitionError as e:
            print(f"{Fore.RED}✗ Mode switch failed: {e} / 模式切换失败{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"{Fore.RED}✗ Unknown error occurred: {e} / 发生未知错误{Style.RESET_ALL}")
            return False

    def show_risk_limits(self) -> None:
        """Show Risk Limits / 显示风险限制"""
        if self.constitution_loader is None:
            print(f"{Fore.YELLOW}Please load constitution file first / 请先加载宪法文件{Style.RESET_ALL}")
            return
        
        try:
            limits = self.constitution_loader.get_risk_limits()
            
            print(f"{Fore.CYAN}Risk Limits Configuration: / 风险限制配置:{Style.RESET_ALL}")
            print(f"  Max Capital Usage: {limits['max_capital_usage']:.1%} / 最大资金使用比率")
            print(f"  Max Single Position: {limits['max_single_position']:.1%} / 单一头寸上限")
            print(f"  Max Sector Exposure: {limits['max_sector_exposure']:.1%} / 单一行业暴露上限")
            print(f"  Max Drawdown Limit: {limits['max_drawdown']:.1%} / 最大回撤限制")
            
        except Exception as e:
            print(f"{Fore.RED}✗ Failed to read risk limits: {e} / 读取风险限制失败{Style.RESET_ALL}")

    def show_market_states(self) -> None:
        """Show Market States Configuration / 显示市场状态配置"""
        if self.constitution_loader is None:
            print(f"{Fore.YELLOW}Please load constitution file first / 请先加载宪法文件{Style.RESET_ALL}")
            return
        
        try:
            states = ["normal_market", "cautious_market", "dangerous_market"]
            
            print(f"{Fore.CYAN}Market State Configuration: / 市场状态配置:{Style.RESET_ALL}\n")
            
            for state in states:
                params = self.constitution_loader.get_market_state_parameters(state)
                if params:
                    print(f"  【{state}】")
                    print(f"    Max Capital Usage: {params['max_capital_usage']:.1%} / 最大资金使用比率")
                    print(f"    Max Single Position: {params['max_single_position']:.1%} / 单一头寸上限")
                    print(f"    Safety Margin: {params['safety_margin_requirement']} / 安全边际要求")
                    if params.get('min_cash_ratio'):
                        print(f"    Min Cash Ratio: {params['min_cash_ratio']:.1%} / 现金比例下限")
                    print()
            
        except Exception as e:
            print(f"{Fore.RED}✗ Failed to read market state configuration: {e} / 读取市场状态配置失败{Style.RESET_ALL}")


def main():
    """Main Function / 主函数"""
    parser = argparse.ArgumentParser(
        description="Uniscanner CLI - Constitution Management and System Control Tool / 宪法管理和系统控制工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available Commands / 可用命令")
    
    # load command
    load_parser = subparsers.add_parser("load", help="Load Constitution File / 加载宪法文件")
    load_parser.add_argument(
        "--path", "-p",
        type=Path,
        help="Constitution file path (default: constitution.yaml) / 宪法文件路径"
    )
    
    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate Constitution Configuration / 验证宪法配置")
    validate_parser.add_argument(
        "--path", "-p",
        type=Path,
        help="Constitution file path (default: constitution.yaml) / 宪法文件路径"
    )
    validate_parser.add_argument(
        "--strict", "-s",
        action="store_true",
        help="Strict mode (warnings count as failure) / 严格模式"
    )
    
    # mode command
    mode_parser = subparsers.add_parser("mode", help="View or Switch System Mode / 查看或切换系统模式")
    mode_parser.add_argument(
        "--switch", "-s",
        type=str,
        choices=["SIMULATION", "DRY_RUN", "LIVE", "EMERGENCY"],
        help="Switch to specified mode / 切换到指定模式"
    )
    mode_parser.add_argument(
        "--reason", "-r",
        type=str,
        default="",
        help="Switch reason / 切换原因"
    )
    mode_parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force switch (skip confirmation) / 强制切换"
    )
    
    # info command
    info_parser = subparsers.add_parser("info", help="Show Constitution Info / 显示宪法信息")
    info_parser.add_argument(
        "--path", "-p",
        type=Path,
        help="Constitution file path (default: constitution.yaml) / 宪法文件路径"
    )
    info_parser.add_argument(
        "--type", "-t",
        type=str,
        choices=["risk", "market"],
        default="risk",
        help="Info type: risk (Risk Limits), market (Market States) / 信息类型"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = CLI()
    
    # Execute command / 执行命令
    if args.command == "load":
        cli.load_constitution(args.path)
    
    elif args.command == "validate":
        if cli.load_constitution(args.path):
            cli.validate_constitution(strict=args.strict)
    
    elif args.command == "mode":
        if args.switch:
            cli.switch_mode(args.switch, reason=args.reason, force=args.force)
        else:
            cli.show_mode()
    
    elif args.command == "info":
        if cli.load_constitution(args.path):
            if args.type == "risk":
                cli.show_risk_limits()
            elif args.type == "market":
                cli.show_market_states()


if __name__ == "__main__":
    main()
