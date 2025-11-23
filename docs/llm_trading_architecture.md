# LLM 自动化投资系统架构概要

> 目标：基于财报 / 新闻 / 宏观 / 行业信息，使用 LLM 做分析，用规则与风控做决策与执行。

---

## 1. 顶层架构

```mermaid
graph TD
    User[👤 你（系统管理员 / 研究员）]

    subgraph G[🧾 宪法 & 治理层 Constitution & Governance]
        CONST[Constitution.yaml<br/>系统最高规则]
        ModeManager[Mode Manager<br/>模式管理 SIM/DRY_RUN/LIVE]
    end

    subgraph D[📥 数据层 Data Layer]
        Ingestion[Data Ingestion<br/>行情/财报/新闻/宏观抓取]
        Cleaning[Data Cleaning<br/>缺失值/时间戳/去重]
        Storage[Data Storage<br/>DB+对象存储+版本]
    end

    subgraph LLM[🧠 LLM 分析层 LLM Agent Layer]
        EarningsAgent[Earnings Agent<br/>财报/电话会议分析]
        NewsAgent[News Agent<br/>新闻/事件分析]
        IndustryAgent[Industry Agent<br/>行业/竞品对比]
        MacroAgent[Macro Agent<br/>宏观环境分析]
        ExplainAgent[Explain Agent<br/>决策解释/总结]
    end

    subgraph DEC[⚖️ 决策与评分层 Scoring & Decision Engine]
        ScoringEngine[Scoring Engine<br/>综合得分/评级]
        SignalGenerator[Signal Generator<br/>Buy/Hold/Sell 信号]
    end

    subgraph RISK[🛡️ 风险控制层 Risk & Portfolio]
        PortfolioBuilder[Portfolio Builder<br/>目标仓位计算]
        RiskManager[Risk Manager<br/>仓位/行业/回撤约束]
    end

    subgraph EXEC[💼 执行层 Execution Layer]
        OrderGenerator[Order Generator<br/>订单生成]
        BrokerAPI[Broker API Adapter<br/>券商适配]
    end

    subgraph MON[📊 监控 & 审计层 Monitoring & Audit]
        Monitor[Realtime Monitor<br/>收益/风险监控]
        Alert[Alert System<br/>告警/通知]
        AuditLog[Audit Logger<br/>完整审计日志]
    end

    User --> CONST
    User --> ModeManager
    ModeManager -->|限制/配置| Ingestion
    ModeManager --> LLM
    ModeManager --> DEC
    ModeManager --> RISK
    ModeManager --> EXEC

    CONST --> ModeManager
    CONST --> RiskManager
    CONST --> EXEC
    CONST --> Monitor

    Ingestion --> Cleaning --> Storage

    Storage --> EarningsAgent
    Storage --> NewsAgent
    Storage --> IndustryAgent
    Storage --> MacroAgent

    EarningsAgent --> ScoringEngine
    NewsAgent --> ScoringEngine
    IndustryAgent --> ScoringEngine
    MacroAgent --> ScoringEngine

    ScoringEngine --> SignalGenerator
    SignalGenerator --> PortfolioBuilder
    PortfolioBuilder --> RiskManager
    RiskManager --> OrderGenerator
    OrderGenerator --> BrokerAPI

    BrokerAPI --> AuditLog
    RiskManager --> AuditLog
    ScoringEngine --> AuditLog
    LLM --> AuditLog

    Monitor --> User
    Alert --> User
```

---

## 2. 日常端到端流程

```mermaid
sequenceDiagram
    participant U as 👤 你
    participant M as 🧾 ModeManager
    participant D as 📥 Data Pipeline
    participant L as 🧠 LLM Agents
    participant S as ⚖️ Scoring Engine
    participant P as 🛡️ Portfolio & Risk
    participant E as 💼 Execution
    participant Mon as 📊 Monitor/Audit

    U->>M: 查看/设置模式（SIM/DRY_RUN/LIVE）
    M->>D: 允许每日任务运行？

    D->>D: 抓取行情/财报/新闻/宏观
    D->>D: 清洗/对齐/存储数据

    D->>L: 传入新财报/新闻/宏观文本
    L->>L: 各 Agent 生成结构化 JSON 分析
    L->>S: 传入 earnings/news/industry/macro scores

    S->>S: 计算综合得分 CompositeScore
    S->>S: 生成 Buy/Hold/Sell 信号
    S->>P: 传入信号 + 当前持仓

    P->>P: Portfolio Builder 生成目标仓位
    P->>P: RiskManager 按宪法裁剪仓位
    P->>E: 传入“合法后的目标仓位”

    E->>E: 计算订单：买入/卖出数量
    E->>E: 应用执行规则（价格/频次校验）
    alt LIVE 模式 & 通过风控
        E->>Broker: 通过 API 发送订单
        Broker-->>E: 返回成交结果
    else DRY_RUN/SIM
        E->>E: 只记录，不真实下单
    end

    E->>Mon: 记录订单与成交日志
    S->>Mon: 记录评分与信号
    L->>Mon: 记录 LLM 输入/输出
    P->>Mon: 记录风险与仓位变化
    Mon->>U: 仪表盘 & 告警
```

---

## 3. LLM Agent 结构

```mermaid
graph TD
    subgraph LLM_Agents[🧠 LLM Agent 层]
        Earnings[Earnings Agent<br/>财报 & 电话会议分析]
        News[News Agent<br/>公司新闻/事件分析]
        Industry[Industry Agent<br/>行业 & 竞品对比]
        Macro[Macro Agent<br/>宏观 & 利率 & CPI]
        Explainer[Explain Agent<br/>生成解释/报告]
    end

    subgraph Input[📥 输入数据]
        Filings[财报正文/10-Q/10-K]
        Transcripts[电话会议纪要]
        NewsText[新闻/公告正文]
        MacroText[宏观事件报道]
        StructuredFacts[结构化财务/行业数据]
    end

    subgraph Output[📤 输出结果]
        EarningsJSON[earnings_score<br/>趋势/风险标记 JSON]
        NewsJSON[news_score<br/>情绪/影响范围 JSON]
        IndustryJSON[industry_score<br/>相对强弱 JSON]
        MacroJSON[macro_risk_level<br/>板块偏好 JSON]
        HumanReport[自然语言解释/投资逻辑报告]
    end

    Input --> Earnings
    Input --> News
    Input --> Industry
    Input --> Macro

    Earnings --> EarningsJSON
    News --> NewsJSON
    Industry --> IndustryJSON
    Macro --> MacroJSON

    EarningsJSON --> Explainer
    NewsJSON --> Explainer
    IndustryJSON --> Explainer
    MacroJSON --> Explainer
    StructuredFacts --> Explainer

    Explainer --> HumanReport
```

---

## 4. 决策 - 风控 - 执行链

```mermaid
graph LR
    Signals[⚖️ Signal Generator<br/>Buy/Hold/Sell 信号]
    PB[Portfolio Builder<br/>目标仓位计算]
    RM[🛡️ Risk Manager<br/>应用宪法风险约束]
    OG[Order Generator<br/>订单生成]
    EC[Execution Checker<br/>执行规则检查]
    API[Broker API<br/>券商接口]

    CONST[🧾 Constitution.yaml<br/>风险/权限/回撤规则]

    Signals --> PB --> RM --> OG --> EC --> API

    CONST --> RM
    CONST --> EC

    subgraph Decisions[决策路径]
        Signals --> PB --> RM
    end

    subgraph RiskControls[风险控制点]
        RM:::risk
        EC:::risk
    end

    classDef risk fill=#ffeeee,stroke=#cc0000,stroke-width=2px;

    RM -->|拒绝 / 裁剪仓位| OG
    EC -->|拒绝订单 / 触发停机| API
```

---

## 5. 模式状态机

```mermaid
stateDiagram-v2
    [*] --> SIMULATION

    SIMULATION: 仿真模式\n回放/回测，不连券商
    DRY_RUN: 影子模式\n连行情，不下真实单
    LIVE: 实盘模式\n自动交易

    SIMULATION --> DRY_RUN: 条件：\n基本流程跑通\n无重大错误
    DRY_RUN --> LIVE: 条件：\n≥4周 SIM\n≥2周 DRY_RUN\n通过风控测试\n人工确认

    LIVE --> DRY_RUN: 手动切换 / Kill Switch
    LIVE --> EMERGENCY: 触发紧急条件（回撤/LLM/技术异常）
    DRY_RUN --> EMERGENCY: 重大技术异常

    EMERGENCY: 紧急模式\n只允许减仓或清仓\n禁止新增仓位

    EMERGENCY --> DRY_RUN: 人工解除\n确认问题根因已排除
```

---

## 6. 治理关系

```mermaid
graph TD
    User[👤 你（最高权限）]

    CONST[🧾 宪法 Constitution.yaml]

    subgraph Governance[治理对象]
        ModeMgr[Mode Manager]
        RiskMgr[Risk Manager]
        Exec[Execution Engine]
        LLM[LLM Agents]
        Dec[Decision Engine]
        Monitor[Monitor & Alert]
    end

    User --> CONST
    User --> ModeMgr
    User --> Monitor

    CONST --> ModeMgr
    CONST --> RiskMgr
    CONST --> Exec

    LLM --> Dec
    Dec --> RiskMgr
    RiskMgr --> Exec

    Monitor --> User
```
