# Uniscanner - LLM驱动的价值投资自动化系统

基于巴菲特投资哲学和市场周期智慧的智能投资系统，使用LLM进行基本面分析。

## 项目状态

🎯 **Phase 0 已完成** - 宪法与治理系统核心实施

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

复制环境配置示例：

```bash
cp .env.example .env
```

编辑 `.env` 文件配置您的环境变量。

### 3. 验证宪法配置

```bash
python cli.py validate
```

### 4. 运行测试

```bash
pytest
```

## 核心功能

### 宪法系统

宪法是系统的最高规则，定义了：

- **风险预算**：最大资金使用比率、单一头寸上限、行业暴露限制
- **市场状态感知**：正常/谨慎/危险市场的自动识别和参数调整
- **企业质量标准**：商业模式、财务健康、管理层评估标准
- **估值原则**：安全边际要求和估值方法
- **紧急规则**：触发器和应对预案
- **执行纪律**：交易最佳实践和价格保护

### 模式管理

系统支持四种运行模式：

- **SIMULATION** - 仿真模式：回放/回测，不连券商
- **DRY_RUN** - 影子模式：连行情，不下真实单
- **LIVE** - 实盘模式：自动交易（需人工确认）
- **EMERGENCY** - 紧急模式：只允许减仓或清仓

### CLI工具

#### 加载宪法

```bash
python cli.py load [--path constitution.yaml]
```

#### 验证宪法

```bash
python cli.py validate [--path constitution.yaml] [--strict]
```

#### 查看当前模式

```bash
python cli.py mode
```

#### 切换模式

```bash
python cli.py mode --switch DRY_RUN --reason "开始影子运行"
```

#### 查看风险限制

```bash
python cli.py info --type risk
```

#### 查看市场状态配置

```bash
python cli.py info --type market
```

## 项目结构

```
uniscanner/
├── src/
│   ├── constitution/      # 宪法模块
│   │   ├── schema.py      # 数据结构定义
│   │   ├── loader.py      # 宪法加载器
│   │   └── validator.py   # 宪法验证器
│   ├── app/               # 应用核心
│   │   ├── mode_manager.py    # 模式管理器
│   │   └── logging_setup.py   # 日志系统
│   └── config/            # 配置管理
│       └── loader.py      # 配置加载器
├── tests/                 # 测试套件
├── docs/                  # 文档
├── mermaid/              # 架构图
├── constitution.yaml      # 宪法配置文件
├── cli.py                # CLI工具
└── requirements.txt      # 依赖列表
```

## Phase 0 实施清单

- ✅ 项目结构和依赖配置
- ✅ 宪法数据结构 (schema.py)
- ✅ 宪法加载器 (loader.py)
- ✅ 日志系统 (logging_setup.py)
- ✅ 模式管理器 (mode_manager.py)
- ✅ 宪法验证器 (validator.py)
- ✅ 配置加载器 (config/loader.py)
- ✅ 测试套件
- ✅ CLI工具

## 验收标准

Phase 0已满足所有验收标准：

- ✅ 成功加载 `constitution.yaml` 无错误
- ✅ 错误配置时能清晰报错并阻止启动
- ✅ 模式切换功能正常且有审计日志
- ✅ LIVE模式有确认机制防止误操作
- ✅ 所有关键路径有测试覆盖
- ✅ CLI工具可以验证宪法和管理模式

## 下一步：Phase 1

Phase 1将实施数据管道，包括：

- 数据抓取（行情/财报/新闻/宏观）
- 数据清洗和对齐
- 数据存储（Parquet + SQLite）
- 每日数据更新流程

## 核心理念

> "规则一：永远不要亏钱；规则二：永远不要忘记规则一"  
> —— 沃伦·巴菲特

本系统严格遵循价值投资原则，以安全边际为核心，注重长期复合增长，避免毁灭性损失。

## 许可证

本项目为个人研究项目。

## 警告

⚠️ **投资有风险，入市需谨慎**

本系统仅供学习和研究使用。任何投资决策都应经过充分的独立思考和风险评估。使用本系统进行实盘交易的任何后果由使用者自行承担。
