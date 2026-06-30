# Contract Approval Agent

企业合同审批路由 Agent —— 基于 LangGraph 的确定性审批流程 + LLM 模糊分类 + HITL 人工确认。

## 这是什么

一个演示项目，展示如何用 Agent 技术增强（而非替代）企业合同审批系统。

**核心论点**：规则引擎覆盖 80% 的标准合同审批路径；Agent 处理规则引擎做不好的 20%——模糊分类、风险识别、流程引导。

**诚实口径**：场景设计参考了综合能源行业的合同审批通用模式，数据全部虚构，Agent 实现是为学习范式自己搭建的。

## 宏观逻辑

### 合同审批的全流程

```
需求立项 → 合同起草 → 会签审查 → 审批决策 → 签署归档 → 履行变更
```

本项目聚焦**审批决策**阶段——合同发起后，如何路由到正确的审批链，并在高风险节点转人工。

### 两种系统的分工

```
┌─────────────────────────────────────────────────┐
│              合同审批系统                          │
│                                                 │
│  ┌──────────────┐   ┌─────────────────────────┐ │
│  │  规则引擎     │   │  Agent 补充层            │ │
│  │  (80% 标准)   │   │  (20% 模糊/复杂)        │ │
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
| 混合板块（跨业务合作） | 无法分类 | LLM 语义判断 |
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
│  │ Triage  │───▶│  RAG    │───▶│    Route     │ │
│  │(规则优先) │    │(SOP检索) │    │(查审批矩阵)  │ │
│  └─────────┘    └─────────┘    └──────────────┘ │
│                                       │          │
│                              ┌────────▼────────┐ │
│                              │   Guardrails    │ │
│                              │ · 项目立项校验   │ │
│                              │ · 跨业务隔离     │ │
│                              └────────┬────────┘ │
│                                       │          │
│                              ┌────────▼────────┐ │
│                              │      HITL      │ │
│                              │ (大额/不可逆)   │ │
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
| **RAG** | 检索 SOP/模板 | SOP 是非结构化文本，适合语义检索 |
| **Route** | 纯代码查表 | 审批矩阵是结构化数据，查表零成本 |
| **Guardrail** | 纯代码条件判断 | 规则明确，不需要 LLM |
| **HITL** | `interrupt()` + `Command(resume=...)` | LangGraph 原生支持，状态自动保存 |
| **Audit Log** | 代码写入 JSONL | append-only，不依赖 LLM |

## 数据设计

> 所有数据均为虚构，仅用于演示 Agent 决策逻辑。

### 审批权限矩阵 (`data/approval_matrix.json`)

```json
{
  "板块": "燃气",
  "合同类型": "设备采购",
  "金额上限": 500000,
  "审批链": ["部门主管", "财务经理", "分公司总经理"],
  "需人工确认": false
}
```

### 合同样本 (`data/contracts.jsonl`)

```json
{
  "id": "C001",
  "test_case": "normal_routing",
  "板块": "燃气",
  "合同类型": "设备采购",
  "金额": 300000,
  "关联项目id": "P001",
  "发起人": "张明",
  "说明": "标准设备采购，金额适中，项目已立项"
}
```

### 四个测试场景

| ID | 场景 | 合同特征 | 预期行为 |
|----|------|----------|----------|
| C001 | 正常审批 | 燃气、设备采购、30万、项目已立项 | 路由到审批链，自动通过 |
| C002 | 大额 HITL | 燃气、设备采购、600万 | 路由到审批链，触发人工确认 |
| C003 | 未立项阻断 | 综合能源、工程施工、项目未评审 | Guardrail 阻断 |
| C004 | 跨业务拦截 | 综合能源、能源管理、跨业务标记 | Guardrail 阻断 |

## 运行

### 安装

```bash
cd Projects/contract-approval-agent
uv sync
cp .env.example .env
# 编辑 .env，填入 LLM API key（HITL 场景需要，其他场景不需要）
```

### 列出所有合同

```bash
uv run python main.py --list
```

```
Available contracts:
  C001 | normal_routing  | 燃气   | ¥   300,000 | 标准设备采购，金额适中，项目已立项
  C002 | amount_hitl     | 燃气   | ¥ 6,000,000 | 大额设备采购，需人工确认
  C003 | project_block   | 综合能源 | ¥ 3,000,000 | 工程施工，关联项目未通过投资评审
  C004 | isolation_block | 综合能源 | ¥ 2,000,000 | 能源管理合同涉及受监管区域，需隔离审查
```

### 运行单个合同

```bash
# 正常审批（自动通过）
uv run python main.py --contract C001

# 大额 HITL（触发人工确认）
uv run python main.py --contract C002

# 未立项阻断
uv run python main.py --contract C003

# 跨业务阻断
uv run python main.py --contract C004
```

### HITL 恢复

```bash
# 第一步：触发中断
uv run python main.py --contract C002
# 输出：⏸  HITL 中断 — 等待人工审批
#       恢复命令: python main.py --contract C002 --resume approved --thread demo-C002

# 第二步：人工审批后恢复
uv run python main.py --contract C002 --resume approved --thread demo-C002
```

### 运行测试

```bash
uv run pytest tests/ -v
```

```
tests/test_trajectories.py::TestNormalRouting::test_status_approved        PASSED
tests/test_trajectories.py::TestNormalRouting::test_approval_chain         PASSED
tests/test_trajectories.py::TestNormalRouting::test_no_hitl                PASSED
tests/test_trajectories.py::TestNormalRouting::test_guardrails_passed      PASSED
tests/test_trajectories.py::TestNormalRouting::test_audit_trajectory       PASSED
tests/test_trajectories.py::TestAmountHitl::test_interrupt_triggered       PASSED
tests/test_trajectories.py::TestAmountHitl::test_interrupt_payload         PASSED
tests/test_trajectories.py::TestAmountHitl::test_resume_approved           PASSED
tests/test_trajectories.py::TestAmountHitl::test_resume_rejected           PASSED
tests/test_trajectories.py::TestProjectBlock::test_status_blocked          PASSED
tests/test_trajectories.py::TestProjectBlock::test_block_reason            PASSED
tests/test_trajectories.py::TestProjectBlock::test_project_guard_failed    PASSED
tests/test_trajectories.py::TestProjectBlock::test_no_hitl                 PASSED
tests/test_trajectories.py::TestIsolationBlock::test_status_blocked        PASSED
tests/test_trajectories.py::TestIsolationBlock::test_block_reason          PASSED
tests/test_trajectories.py::TestIsolationBlock::test_isolation_guard_failed PASSED
tests/test_trajectories.py::TestIsolationBlock::test_project_guard_passed  PASSED

17 passed
```

## 90 秒讲解

> 这是我基于综合能源行业合同审批通用模式搭的练手 agent。
>
> 难点不是调 API，是把审批的真实复杂度建模——四板块、多级审批、业务法务财务会签、项目-合同耦合。我用 LangGraph 的图而不是纯 agent，因为审批要确定性和可审计。大额和不可逆操作走 interrupt() 中断等人工确认。受监管业务和竞争性业务之间加了数据隔离 guardrail。全程 append-only log。
>
> 但 agent 不是替代规则引擎。80% 的标准合同走固定模板和固定审批链，不需要 agent。agent 处理的是规则引擎做不好的 20%——混合板块的分类判断、条款级的风险识别、新人不知道流程时的 SOP 引导。
>
> 数据全部虚构，覆盖正常路由、超额、未立项阻断、跨业务拦截四类分支。

## 8 个「为什么」

### 为什么不用纯 Agent？

纯 Agent（让 LLM 自主决定每一步）在审批场景中不可靠——审批需要确定性、可审计、可回溯。LLM 的输出是概率性的，同一个输入可能产生不同结果。用 LangGraph 的图结构把流程固化，只在需要判断力的环节（分类、风险识别）调用 LLM。

### 为什么 LangGraph？

审批流程的本质是**有状态的确定性工作流** + **条件触发的人工介入**。LangGraph 的三个能力完美匹配：
1. **图结构**：节点 + 条件边，流程显式可审计
2. **`interrupt()`**：任意位置暂停等人工，状态自动保存
3. **Checkpointing**：`thread_id` 作为持久指针，可跨会话恢复

### 为什么 Rule Engine + Agent？

规则引擎处理 80% 的标准路径（零成本、零幻觉），Agent 处理 20% 的模糊/复杂场景（需要语义理解）。两者共享同一份数据（审批矩阵、项目台账），Agent 不重复实现规则引擎已有的能力。

### 为什么 HITL？

合同审批中有些节点是**不可逆的**（签署、大额支付、对外担保）。这些节点不能让 Agent 自动执行——必须等人工确认。LangGraph 的 `interrupt()` 让这变得简单：暂停、返回 payload 给调用方、等人工决策后 `Command(resume=...)` 恢复。

### 为什么 Guardrails？

审批有两个硬约束不能靠 LLM 判断：
1. **项目-合同耦合**：项目未立项，合同不得审批——这是业务规则，不是「建议」
2. **跨业务隔离**：受监管业务与竞争性业务之间需要数据隔离——这是合规要求

Guardrail 用纯代码实现（查表 + 条件判断），输出写入 State（不抛异常），方便 tracing 和 evaluation。

### 为什么用 Pydantic State？

Graph 的所有节点共享一份 State。用 Pydantic 定义 schema 的好处：
1. **类型安全**：IDE 自动补全，运行时自动验证
2. **序列化**：State 可以存数据库、传给前端、写入日志
3. **可读性**：State 的字段就是业务语义的映射

### 为什么不是 MCP？

MVP 阶段工具用自定义函数（`get_approval_chain()`、`check_project_approved()`）。MCP 是工具连接的标准协议，生产环境应该用——但 MVP 的价值是跑通流程、展示设计判断，不是展示协议集成。

### 为什么使用合成数据？

合规要求。所有数据均为虚构——板块名称、合同类型、人名、组织结构都是为了演示 Agent 决策逻辑而编造的，不代表任何真实企业的业务架构。数据仅覆盖四个典型分支（正常、大额、未立项、跨业务），验证 Agent 的完整行为路径。

## 项目结构

```
contract-approval-agent/
├── README.md              ← 你在读的这个
├── TODO.md                ← 实现计划（Phase 0-7 已完成）
├── pyproject.toml         ← 依赖（langgraph, langchain, pydantic）
├── .env.example           ← 环境变量模板
├── main.py                ← CLI 入口（--list / --contract / --resume）
├── src/
│   ├── state.py           ← Pydantic State（ContractState + AuditEntry + GuardrailResult）
│   ├── graph.py           ← LangGraph 图组装（6 节点 + 条件边）
│   ├── config.py          ← LLM Provider 配置
│   ├── tools.py           ← 工具函数（查审批矩阵、查项目、查 SOP）
│   └── nodes/
│       ├── triage.py      ← 分类（规则优先）
│       ├── rag.py         ← SOP 检索
│       ├── route.py       ← 审批链路由（查表）
│       ├── guardrails/
│       │   ├── project_guard.py   ← 项目立项校验
│       │   └── isolation_guard.py ← 跨业务隔离校验
│       ├── hitl.py        ← 人工确认（interrupt/resume）
│       └── audit_log.py   ← append-only JSONL
├── data/                  ← 虚构数据（生成脚本在 scripts/）
│   ├── approval_matrix.json
│   ├── contracts.jsonl
│   ├── projects.jsonl
│   └── templates/
├── tests/
│   └── test_trajectories.py  ← 17 个 trajectory 测试
├── scripts/
│   └── generate_data.py   ← 合成数据生成
└── docs/
    └── interview-narrative.md  ← 面试叙事文档
```

## 参考信源

| 信源 | 用途 |
|------|------|
| Anthropic「Building Effective Agents」 | 架构哲学：从简单开始，按需增加复杂度 |
| LangGraph HITL docs | `interrupt()` + `Command(resume=...)` 实现 |
| OpenAI Agents SDK airline example | Triage + Handoff 模式参考 |
| Yao et al. ICLR 2023 (ReAct) | 推理范式：Thought→Action→Observation |
