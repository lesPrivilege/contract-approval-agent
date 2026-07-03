# Contract Approval Agent

合同审批路由 Agent：结构化决策 + 分层防御。

## 这是什么

演示项目：用 Agent 技术增强（而非替代）企业合同审批系统。

**核心论点**：合同审批路由 Agent：结构化决策 + 分层防御。核心判断抽象为 model-tool loop，LangGraph 状态图是编排外壳；防御分三层——LLM 置信度阈值（< 0.8 转人工）、三道纯代码护栏（相对方黑名单 / 项目预算上限 / 跨板块隔离）、HITL 兜底。机器能判断的自动判断，没把握的转人工，风险合同自动拦截。

**诚实口径**：场景设计参考多板块企业合同审批的通用模式，数据全部虚构。

> **配套项目**：本项目是三个项目之一——`compliance-review-agent`（合规审查，RAG+推理）展示知识密集型场景的互补架构，`agent-quality-workbench`（PM 侧评估工具）提供立项评分和跨 agent 质量仪表盘。

## 宏观逻辑

### 合同审批全流程

```
需求立项 → 合同起草 → 会签审查 → 审批决策 → 签署归档 → 履行变更
```

本项目聚焦**审批决策**——合同发起后，如何路由到正确的审批链，并在高风险节点转人工。

### 两种系统的分工

```
┌─────────────────────────────────────────────────┐
│              合同审批系统                          │
│                                                 │
│  ┌──────────────┐   ┌─────────────────────────┐ │
│  │  规则引擎     │   │  Agent 补充层            │ │
│  │  (标准路径)   │   │  (边界场景)              │ │
│  │              │   │                         │ │
│  │ · 固定模板    │   │ · 模糊分类（混合板块）    │ │
│  │ · 固定字段    │   │ · 条款级风险识别         │ │
│  │ · 固定审批链  │   │ · SOP 检索引导          │ │
│  │ · 加签兜底    │   │ · 例外情况建议          │ │
│  └──────────────┘   └─────────────────────────┘ │
│                                                 │
│  共享数据：审批矩阵 / 合同模板 / 项目台账 / 日志  │
└─────────────────────────────────────────────────┘
```

### Agent 的价值定位

| 场景 | 规则引擎 | Agent |
|------|----------|-------|
| 标准合同（类型明确、金额清晰） | 直接路由，零成本 | 没必要用 |
| 混合板块（跨板块合作） | 无法分类 | LLM 语义判断 |
| 条款风险（无限责任、长期合同） | 只能 catch 预设规则 | 条款语义理解 |
| 新人不知道流程 | 自己查 SOP | Agent 主动引导 |

## 架构

### 组件图

```
合同发起
   │
   ▼
┌──────────────────────────────────────────────────┐
│                LangGraph 图                       │
│                                                  │
│  ┌─────────┐    ┌─────────┐    ┌──────────────┐ │
│  │ Triage  │───▶│ SOP检索  │───▶│    Route     │ │
│  │(规则优先) │    │(精确匹配) │    │(查审批矩阵)  │ │
│  └─────────┘    └─────────┘    └──────────────┘ │
│                                       │          │
│                              ┌────────▼────────┐ │
│                              │   Guardrails    │ │
│                              │ · 项目评审校验   │ │
│                              │ · 预算上限校验   │ │
│                              │ · 跨板块隔离     │ │
│                              └────────┬────────┘ │
│                                       │          │
│                              ┌────────▼────────┐ │
│                              │      HITL      │ │
│                              │ (大额/担保/关联) │ │
│                              │  interrupt()   │ │
│                              └────────┬────────┘ │
│                                       │          │
│                              ┌────────▼────────┐ │
│                              │   Audit Log    │ │
│                              │ (append-only)  │ │
│                              └────────────────┘ │
└──────────────────────────────────────────────────┘
```

### 状态流转

```
Draft ──▶ Triaged ──▶ Retrieved ──▶ Routed ──▶ Guard Checked ──▶ Waiting HITL ──▶ Approved
                                           │                         │
                                           └──▶ Blocked             └──▶ Rejected
```

### 每个节点的实现方式

| 节点 | 方式 | 为什么 |
|------|------|--------|
| **Triage** | 规则优先 + LLM 兜底 | 标准路径确定性，边界场景用 LLM 判断 |
| **Clause Extraction** | LLM 结构化输出（`条款描述` 非空时） | 从自由文本抽取风险标记，低置信度触发 HITL |
| **SOP 检索** | 精确 key 匹配模板 | 模板库 key 齐全、命名规范，精确匹配比向量检索更可控 |
| **Route** | 纯代码查表（支持成熟度分流） | 审批矩阵是结构化数据，查表零成本 |
| **Guardrail** | 纯代码条件判断 | 规则明确，不需要 LLM |
| **HITL** | `interrupt()` + `Command(resume=...)` | 高风险或低置信度节点暂停，状态自动保存 |
| **Audit Log** | 代码写入 JSONL | append-only，不依赖 LLM |

## 数据设计

> 所有数据均为虚构。板块 A-D 代表不同业务原型：A 受监管型、B 投资驱动型、C 竞争型、D 支撑型。

### 审批权限矩阵 (`data/approval_matrix.json`)

```json
{
  "板块": "B",
  "板块标记": "投资驱动",
  "合同类型": "投资合作类",
  "金额上限": 999999999,
  "要求成熟度": "high",
  "审批链": ["投资板块负责人", "财务负责人", "分管副总"],
  "需人工确认": false
}
```

矩阵支持三种分档维度：
- **金额分档**：不同金额阈值对应不同审批链
- **成熟度分流**：B 板块投资合作类按「high/low」走不同审批路径
- **类型分档**：不同合同类型激活不同职能组合

### 测试场景

| ID | 场景 | 合同特征 | 预期行为 |
|----|------|----------|----------|
| C001 | 正常审批 | A、采购类、30万、项目已立项 | 路由 → 自动通过 |
| C002 | 大额 HITL | A、采购类、600万 | 路由 → 人工确认 |
| C003 | 未立项阻断 | B、工程类、项目未评审 | Guardrail 阻断 |
| C004 | 跨板块拦截 | B、服务类、跨板块标记 | Guardrail 阻断 |
| C005 | C 板块正常路由 | C、服务类、20万 | 路由 → 自动通过 |
| C006 | D 板块担保 HITL | D、担保类、含担保条款 | 路由 → 人工确认 |
| C007 | 成熟度分流-高 | B、投资合作类、高成熟度 | 高效链（投→财→副总）→ 自动通过 |
| C008 | 成熟度分流-低 | B、投资合作类、低成熟度 | 审慎链（投→总→上级）→ 人工确认 |
| C009 | 预算超额阻断 | B、工程类、项目已评审但超预算 | Guardrail 阻断（超预算上限） |
| C010 | 关联方 HITL | A、采购类、关联方标记 | 路由 → 人工确认（关联交易增强审查） |
| C011 | 黑名单阻断 | A、采购类、对方状态=黑名单 | counterparty_guard 拦截 |
| C012 | LLM 条款抽取-高置信 | A、采购类、条款描述清楚 | LLM 抽取 → 高置信度 → 自动通过 |
| C013 | LLM 条款抽取-低置信 | B、服务类、条款描述模糊 | LLM 抽取 → 低置信度 → HITL |
| C014 | LLM 识别黑名单 | A、采购类、条款描述含黑名单 | LLM 抽取 → 对方状态=黑名单 → 拦截 |

### LLM 条款抽取机制

`clause_extraction_node` 在 `triage` 之后、`rag` 之前插入。当合同的 `条款描述` 字段非空时，调用 LLM 从自由文本中抽取风险标记（不可逆/担保/跨业务/关联方/对方状态）。抽取结果覆盖合同原有标记，下游 guardrail 和 HITL 基于 LLM 输出判断。

**置信度机制**：LLM 返回 `confidence` 分数。`< 0.8` 时 `extraction_low_confidence=True`，触发 HITL（reason："LLM 条款抽取置信度低，需人工复核抽取结果"）。这是 LLM 自身的不确定性触发人工介入——不只是业务规则能触发 HITL。阈值从初始 0.7 上调至 0.8，因为 subagent 验证发现 C013（条款模糊样本）的置信度为 0.75——高于 0.7 不会被拦截，但这类中等模糊的条款确实应该触发人工复核。

`条款描述` 为空时跳过此节点，沿用手写标记——现有确定性测试不受影响。LLM 测试需 `OPENAI_API_KEY`，无 key 时自动跳过。

### 分类节点：规则优先、LLM 兜底

分类节点规则优先、LLM 兜底：已知板块 × 合同类型组合直接查表；未命中时由 LLM 结构化输出分类结果与置信度。兜底路径在审计日志中以 `method="llm_fallback"` 标记，可与规则路径区分统计。

### SOP 检索：为什么是精确匹配

SOP 检索用精确 key 匹配而非向量检索，是选型而非省事：模板库 key 齐全、命名规范，embedding 解决的是语料没结构的问题——语料本身有结构时，引入向量只会增加不确定性。

## 运行

```bash
cd contract-approval-agent
uv sync
cp .env.example .env

uv run python main.py --list                    # 列出所有合同
uv run python main.py --contract C001           # 正常审批
uv run python main.py --contract C002           # HITL 中断
uv run python main.py --contract C002 --resume approved --thread demo-C002  # 恢复
uv run pytest tests/ -v                         # 44 passed, 8 skipped（无 API key 时）
```

## 设计决策

### 为什么不用纯 Agent？

审批需要确定性、可审计、可回溯，所以不能让 LLM 自由决定每一步。本项目把核心判断拆成受控的 model-tool loop：LLM 负责模糊分类和条款抽取，工具负责查表、检索、guardrail、HITL 和审计日志。

### 为什么这里还用了 LangGraph？

这版实现需要一个清楚可审计的状态外壳，所以用 LangGraph 把 6 个节点和条件边显式写出来：
1. **图结构**：节点 + 条件边，流程显式可审计
2. **`interrupt()`**：任意位置暂停等人工，状态自动保存
3. **Checkpointing**：`thread_id` 作为持久指针，可跨会话恢复

但面试叙事里不把 LangGraph 当成架构中心。它只是当前可读、可测的编排外壳；真正可迁移的设计是「模型判断 + 工具执行 + guardrail/HITL 收口」这一层。

### 为什么 Rule Engine + Agent？

规则引擎处理标准路径（零成本、零幻觉），Agent 处理边界场景（需要语义理解）。两者共享同一份数据，Agent 不重复实现规则引擎已有的能力。

### 为什么 HITL？

合同审批中有些节点是**不可逆的**（签署、大额支付、对外担保）。这些节点不能让 Agent 自动执行——必须等人工确认。

### 为什么 Guardrails？

审批有硬约束不能靠 LLM 判断：项目-合同耦合、预算上限校验、跨板块隔离。Guardrail 用纯代码实现，输出写入 State，方便 tracing。

### 为什么用 Pydantic State？

1. **类型安全**：IDE 自动补全，运行时自动验证
2. **序列化**：State 可以存数据库、传给前端、写入日志
3. **可读性**：State 的字段就是业务语义的映射

## 项目结构

```
contract-approval-agent/
├── main.py                ← CLI 入口
├── src/
│   ├── state.py           ← Pydantic State
│   ├── graph.py           ← LangGraph 图组装（6 节点 + 条件边）
│   ├── tools.py           ← 工具函数（查审批矩阵、查项目、查 SOP）
│   └── nodes/
│       ├── triage.py      ← 分类（规则优先）
│       ├── rag.py         ← SOP 检索（精确匹配）
│       ├── route.py       ← 审批链路由（含成熟度分流）
│       ├── guardrails/
│       │   ├── counterparty_guard.py   ← 相对方资信校验
│       │   ├── project_guard.py        ← 项目评审 + 预算上限校验
│       │   └── isolation_guard.py      ← 跨板块隔离校验
│       ├── hitl.py        ← 人工确认（interrupt/resume）
│       └── audit_log.py   ← append-only JSONL
├── data/
│   ├── approval_matrix.json
│   ├── contracts.jsonl
│   ├── projects.jsonl
│   └── templates/
└── tests/
    └── test_trajectories.py  ← 52 个 trajectory 测试（44 deterministic + 8 LLM，无 key 时跳过）
```

## 参考信源

| 信源 | 用途 |
|------|------|
| Anthropic「Building Effective Agents」 | 架构哲学：从简单开始，按需增加复杂度 |
| LangGraph HITL docs | `interrupt()` + `Command(resume=...)` 实现 |
| OpenAI Agents SDK airline example | Triage + Handoff 模式参考 |
| Yao et al. ICLR 2023 (ReAct) | 推理范式：Thought→Action→Observation |

## 相关项目

本仓库的 audit_log 由 [agent-quality-workbench](https://github.com/lesPrivilege/agent-quality-workbench) 单向只读消费——评估器不侵入被评估对象。
