# 快速开始指南

## 🚀 Phase 0 系统已就绪

恭喜！Phase 0 的宪法与治理系统已经完成并可以使用。

## 📦 安装

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 验证安装
python cli.py --help
```

## 🎯 核心功能

### 1. 加载和验证宪法

```bash
# 加载宪法配置
python cli.py load

# 验证宪法配置
python cli.py validate
```

### 2. 查看配置信息

```bash
# 查看风险限制
python cli.py info --type risk

# 查看市场状态配置
python cli.py info --type market
```

### 3. 管理系统模式

```bash
# 查看当前模式
python cli.py mode

# 切换到DRY_RUN模式（需要先在SIMULATION模式）
python cli.py mode --switch DRY_RUN --reason "准备影子运行"

# 切换到LIVE模式（需要确认）
python cli.py mode --switch LIVE --reason "开始实盘" --force
```

## 📋 系统模式说明

| 模式 | 说明 | 用途 |
|------|------|------|
| **SIMULATION** | 仿真模式 | 回放/回测，不连券商 |
| **DRY_RUN** | 影子模式 | 连行情，不下真实单 |
| **LIVE** | 实盘模式 | 自动交易（需确认） |
| **EMERGENCY** | 紧急模式 | 只允许减仓或清仓 |

## 🔒 安全机制

### 模式切换限制

```
SIMULATION → DRY_RUN ✅
DRY_RUN → LIVE ✅ (需确认)
SIMULATION → LIVE ❌ (不允许直接切换)
任何模式 → EMERGENCY ✅ (紧急触发)
```

### LIVE模式确认

切换到LIVE模式时，系统会要求输入 `YES` 进行确认：

```bash
$ python cli.py mode --switch LIVE
⚠️  警告: 即将切换到实盘模式 (LIVE)！
这将允许系统进行真实交易。
是否确认切换？(输入 'YES' 继续): YES
✓ 模式切换成功
```

## 📊 宪法配置

系统的核心配置位于 `constitution.yaml`，包含：

- **风险预算**：资金使用比率、头寸限制
- **市场状态感知**：自动调整不同市场条件下的参数
- **企业质量标准**：投资决策标准
- **估值原则**：安全边际要求
- **紧急规则**：异常情况应对
- **执行纪律**：交易最佳实践

## 🧪 运行测试

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_mode_manager.py -v

# 查看代码覆盖率
pytest --cov=src --cov-report=html
```

## 📝 审计日志

所有重要操作都会记录在审计日志中：

```bash
# 日志位置
logs/audit_YYYYMMDD.jsonl  # 审计日志
logs/app_YYYYMMDD.log      # 应用日志
```

## 🔧 环境配置（可选）

创建 `.env` 文件来自定义配置：

```bash
# 系统模式
SYSTEM_MODE=SIMULATION

# 日志级别
LOG_LEVEL=INFO

# 日志目录
LOG_DIR=logs

# 宪法文件路径
CONSTITUTION_PATH=constitution.yaml
```

## 💡 使用示例

### 每日启动检查

```bash
# 1. 验证宪法配置
python cli.py validate

# 2. 检查当前模式
python cli.py mode

# 3. 查看风险限制
python cli.py info --type risk
```

### 模式切换流程

```bash
# 回测完成后
python cli.py mode --switch DRY_RUN --reason "回测通过，开始影子运行"

# 影子运行2周后
python cli.py mode --switch LIVE --reason "影子运行稳定，启动实盘" --force
```

### 紧急情况处理

如果需要紧急停止交易，通过代码触发EMERGENCY模式：

```python
from src.app.mode_manager import ModeManager, SystemMode

# 触发紧急模式
manager = ModeManager(current_mode=SystemMode.LIVE)
manager.trigger_emergency("市场异常波动")
```

## 📚 更多文档

- [README.md](README.md) - 项目总览
- [PHASE0_COMPLETED.md](PHASE0_COMPLETED.md) - Phase 0完成总结
- [docs/llm_trading_architecture.md](docs/llm_trading_architecture.md) - 系统架构
- [docs/constitution_phase0_plan.md](docs/constitution_phase0_plan.md) - Phase 0实施计划

## ✅ 下一步

Phase 0 已完成，系统已具备基础的治理能力。接下来：

1. **Phase 1**：实施数据管道（行情/财报/新闻抓取）
2. **Phase 2**：实现LLM分析Agent
3. **Phase 3**：构建评分与信号系统
4. **Phase 4**：实现风险控制和组合管理
5. **Phase 5**：对接券商API执行交易

## 🎉 恭喜！

您已经完成了Uniscanner系统的第一阶段！系统现在具备了：

- ✅ 完整的宪法配置系统
- ✅ 安全的模式管理机制
- ✅ 结构化日志和审计功能
- ✅ 命令行管理工具
- ✅ 测试覆盖和验证

**准备好进入Phase 1了吗？** 🚀

