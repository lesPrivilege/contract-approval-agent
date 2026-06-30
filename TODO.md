# TODO · Contract Approval Agent MVP

## 设计决策速查

在开工前，先回答每个 Phase 里的隐含决策：

| 决策 | 选择 | 理由 |
|------|------|------|
| Triage 用什么方式？ | 规则优先 + LLM 兜底 | 标准路径确定性 + 边界场景灵活性 |
| RAG 检索失败怎么办？ | 标记 `sop_missing: True`，继续流程 | 不阻断，但记录 |
| Guardrail 输出什么格式？ | 写入 State（不抛异常） | 方便 tracing 和 evaluation |
| `interrupt()` payload 包含什么？ | 合同摘要 + 风险标记 + 审批链 | 让人工有足够信息做决策 |
| 人工驳回后怎么走？ | 状态变 Rejected，写 audit log，结束 | 不继续走审批链 |
| 每个节点用什么方式？ | Triage/RAG=LLM，Route/Guard/Audit=纯代码 | 最简单方案优先 |

---

## Phase 0：项目初始化（P0）

- [x] 创建项目目录结构
- [ ] 初始化 Python 项目（uv）
- [ ] 配置 LangGraph + LangChain
- [ ] 配置可切换 LLM Provider（环境变量）
- [ ] 添加基础 logging
- [ ] main.py 入口（可启动但不做业务）

验收：`uv run python main.py` 正常启动

---

## Phase 1：业务数据（P0）

- [x] approval_matrix.json（41 条，覆盖 4 板块核心分类）
- [x] generate_data.py 脚本（从 reference 脱敏生成）
- [x] contracts.jsonl（10 条，4 种场景各 2-3 条）
- [x] projects.jsonl（8 个项目，7 已立项 + 1 未立项）
- [x] templates/（4 个 SOP 模板，按板块+法理类型）

数据要求：
- 每条合同带 `test_case` 字段标注场景
- 覆盖：normal_routing / amount_hitl / project_block / isolation_block

验收：`uv run python scripts/generate_data.py` 生成全部数据 ✓

---

## Phase 2：Graph State（P0）

- [ ] 定义 ContractState（Pydantic BaseModel）
- [ ] 字段：contract / project / approval_route / sop / risks / current_step / audit_log / status / interrupt_reason / human_decision / human_comment / guardrail_results
- [ ] 状态流转：Draft → Triaged → Retrieved → Routed → Guard Checked → Waiting HITL → Approved / Rejected / Blocked

验收：State 可序列化（`state.model_dump()`）

---

## Phase 3：Graph（P0）

- [ ] Triage 节点（规则优先 + LLM 兜底）
- [ ] RAG 节点（向量检索 SOP）
- [ ] Route 节点（查 approval_matrix.json）
- [ ] 条件边：guard_passed → HITL / Route / Blocked
- [ ] 图组装：StateGraph + 节点 + 边

验收：`graph.compile()` 成功

---

## Phase 4：Guardrails（P0）

- [ ] Project Guard：查 projects.jsonl，未立项 → status=blocked
- [ ] Isolation Guard：查合同的跨业务标记 → status=blocked
- [ ] 统一 GuardrailResult 格式写入 State

验收：未立项合同被阻断；跨业务合同被阻断

---

## Phase 5：HITL（P0）

- [ ] HITL 节点：`interrupt(payload)` 暂停
- [ ] payload 包含：合同摘要 + 风险标记 + 审批链
- [ ] 恢复：`Command(resume=decision)` 写入 human_decision
- [ ] 驳回流程：status=Rejected，写 audit log，结束

验收：大额合同触发 HITL；恢复后继续执行；驳回后流程结束

---

## Phase 6：Audit（P1）

- [ ] AuditEntry schema（timestamp / node / action / input_summary / output_summary / decision / duration_ms）
- [ ] append-only JSONL 写入
- [ ] 每个节点执行后自动记录

验收：完整 trace 可回放（`cat data/audit_log.jsonl`）

---

## Phase 7：Evaluation（P1）

- [x] Case 1：正常合同 → Approved，不走 HITL
- [x] Case 2：未立项 → Blocked
- [x] Case 3：大额 → HITL → Resume → Approved
- [x] Case 4：跨业务 → Blocked

验收：`uv run pytest tests/ -v` 全部通过 ✓（17/17）

---

## Phase 8：README（P0）

- [x] 8 个「为什么」
- [x] 架构图（ASCII）
- [x] 状态图
- [x] 运行方式（含实际命令和输出）
- [x] 90 秒讲解
- [x] 项目结构

验收：README 可独立阅读 ✓

---

## Phase 9：可选增强（P2）

- [ ] LangSmith tracing
- [ ] DSPy 分类
- [ ] MCP Tool
- [ ] OTel

---

## Don't Do

- 多租户 / 数据库 / 用户系统 / 权限系统
- 前端页面 / 真正 ERP 集成 / 真正 MCP Server
- Kubernetes / Docker / OAuth / 分布式 / 微服务
