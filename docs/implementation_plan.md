# LLM 基本面自动投资系统 —— 实施总体计划（Implementation Plan）

> 目标：从 0 到 1 搭建一个 **安全、可控、可审计** 的 LLM 驱动基本面投资系统，严格受《宪法》和架构约束。

---

## 0. 总体原则

- **安全优先**：任何阶段未通过风控/测试，一律不进入自动实盘。
- **小步快跑**：先打基础（数据 → Agent → 决策 → 风控），再考虑优化收益。
- **严格分层**：数据、LLM、决策、风控、执行、监控模块边界清晰。
- **全程可追溯**：所有关键步骤写日志、版本号、可回放。

---

## 1. 范围与目标

### 1.1 初始范围（V1）

- 市场：美股（先做 S&P500 子集）。
- 工具：股票多头。
- 频率：日级 / 周级调仓。
- 数据：行情、财报文本、新闻、宏观新闻。
- 功能：
  - 每日数据更新
  - 股票评分 + Buy/Hold/Sell 信号
  - 目标仓位 → DRY_RUN 订单
  - 审计与监控

### 1.2 非目标

- 高频交易
- 期权 / 衍生品
- 杠杆 / 做空
- 高频技术指标

---

## 2. 技术栈 & 项目结构

### 2.1 技术栈

- Python 3.11+
- LLM SDK（OpenAI / DeepSeek）
- pandas, numpy
- Parquet / SQLite
- pydantic / yaml
- logging, Streamlit（选）

### 2.2 项目结构建议

```
repo_root/
  constitution/
    constitution_v1.yaml
  docs/
    llm_trading_architecture.md
  src/
    config/
    constitution/
    data/
    agents/
    decision/
    risk/
    execution/
    monitoring/
    app/
  tests/
```

---

## 3. 分阶段实施

### Phase 0：宪法加载

- 实现 `constitution/loader.py`，读 YAML → 对象。
- 实现校验器 `validator.py`。
- 单测：字段缺失/范围错误。

验收：配置统一、错误可检测。

---

### Phase 1：数据管道

- `ingestion.py`：行情/财报/新闻抓取。
- `cleaning.py`：对齐/去重/缺失标记。
- `storage.py`：Parquet + SQLite。
- `daily_pipeline.py`：数据更新。

验收：一个月数据可重建，无缺失崩溃。

---

### Phase 2：LLM Agents

- BaseAgent：文本 → JSON。
- Earnings / News / Industry / Macro / Explain Agent。
- JSON Schema 校验 + 自动重试。
- 小规模手工验证。

验收：单股票完整 JSON 输出、错误可控。

---

### Phase 3：评分与信号

- `scoring_engine.py`：组合得分。
- `signal_generator.py`：阈值 → Buy/Hold/Sell。
- 读取权重与阈值来自配置/宪法。

验收：任意输入 → 稳定得分与信号。

---

### Phase 4：组合 & 风控

- `portfolio_builder.py`：目标仓位（未风控）。
- `risk_manager.py`：
  - max_single_position
  - max_sector_exposure
  - max_equity_exposure
- 对极端仓位正确裁剪。

验收：所有输出满足宪法限制。

---

### Phase 5：订单与执行

- `order_generator.py`：仓位差值 → 股数。
- `execution_engine.py`：
  - LIVE：对券商 API 下单
  - DRY_RUN：记录不执行
- 执行检查：订单金额/上限。

验收：DRY_RUN 全流程跑通。

---

### Phase 6：监控与审计

- `audit_logger.py`：LLM 输入、输出、评分、仓位、订单 → trace_id。
- `monitor.py`：收益、仓位、风险、异常。
- Streamlit 初步仪表盘。

验收：任意一次决策可 100% 回溯。

---

### Phase 7：回测 → DRY_RUN → 小额实盘

- 回测历史 1–3 年。
- DRY_RUN 连续 2–4 周。
- 小额实盘（总资产 5–10%）。
- 异常自动 Kill Switch。

验收：稳定、安全、可控。

---

## 4. 风险控制关键点

- **数据风险**：缺数据 → 不决策。
- **模型风险**：LLM 不直接下单。
- **执行风险**：额度限制 + 审计。
- **系统风险**：模式状态机 + Kill Switch。
- **异常风险**：EMERGENCY 模式。

---

## 5. 最终 Checklist（极简）

1. [ ] 宪法加载  
2. [ ] 数据管道  
3. [ ] Agents  
4. [ ] 评分/信号  
5. [ ] 组合 + 风控  
6. [ ] DRY_RUN 执行  
7. [ ] 审计 + 监控  
8. [ ] 回测 → DRY_RUN → 实盘

---

## 6. 下一步建议

> 标准下一步：创建代码目录 + 完成 `constitution/loader.py` 骨架文件。

