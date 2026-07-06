// Auto-generated from data/contracts.jsonl + data/audit_log.jsonl. Regenerate with scripts/build_demo_data.py.
const CONTRACTS = [
  {
    "id": "C001",
    "test_case": "normal_routing",
    "板块": "A",
    "合同类型": "采购类",
    "金额": 300000,
    "关联项目id": "P001",
    "发起人": "张明",
    "对方状态": "正常",
    "条款标记": {
      "不可逆": false,
      "担保": false,
      "跨业务": false
    },
    "说明": "标准采购，金额适中，项目已立项",
    "hasTrace": true,
    "outcome": "auto_approved",
    "category": "approved",
    "hitl": false,
    "blockedReason": null
  },
  {
    "id": "C002",
    "test_case": "amount_hitl",
    "板块": "A",
    "合同类型": "采购类",
    "金额": 6000000,
    "关联项目id": "P002",
    "发起人": "李芳",
    "对方状态": "正常",
    "条款标记": {
      "不可逆": false,
      "担保": false,
      "跨业务": false
    },
    "说明": "大额采购，需人工确认",
    "hasTrace": true,
    "outcome": "approved",
    "category": "hitl",
    "hitl": true,
    "blockedReason": null
  },
  {
    "id": "C003",
    "test_case": "project_block",
    "板块": "B",
    "合同类型": "工程类",
    "金额": 3000000,
    "关联项目id": "P_NOT_APPROVED",
    "发起人": "王强",
    "对方状态": "正常",
    "条款标记": {
      "不可逆": false,
      "担保": false,
      "跨业务": false
    },
    "说明": "工程合同，关联项目未通过评审",
    "hasTrace": true,
    "outcome": "blocked",
    "category": "blocked",
    "hitl": false,
    "blockedReason": "项目未通过"
  },
  {
    "id": "C004",
    "test_case": "isolation_block",
    "板块": "B",
    "合同类型": "服务类",
    "金额": 2000000,
    "关联项目id": "P003",
    "发起人": "赵伟",
    "对方状态": "正常",
    "条款标记": {
      "不可逆": false,
      "担保": false,
      "跨业务": true
    },
    "说明": "跨板块服务合同，需隔离审查",
    "hasTrace": true,
    "outcome": "blocked",
    "category": "blocked",
    "hitl": false,
    "blockedReason": "阻断: 需合规审查"
  },
  {
    "id": "C005",
    "test_case": "c_sector_routing",
    "板块": "C",
    "合同类型": "服务类",
    "金额": 200000,
    "关联项目id": null,
    "发起人": "孙磊",
    "对方状态": "正常",
    "条款标记": {
      "不可逆": false,
      "担保": false,
      "跨业务": false
    },
    "说明": "C板块标准服务合同，正常路由",
    "hasTrace": true,
    "outcome": "auto_approved",
    "category": "approved",
    "hitl": false,
    "blockedReason": null
  },
  {
    "id": "C006",
    "test_case": "d_sector_guarantee",
    "板块": "D",
    "合同类型": "担保类",
    "金额": 1000000,
    "关联项目id": null,
    "发起人": "周婷",
    "对方状态": "正常",
    "条款标记": {
      "不可逆": false,
      "担保": true,
      "跨业务": false
    },
    "说明": "D板块担保合同，命中担保类高风险HITL分支",
    "hasTrace": true,
    "outcome": "approved",
    "category": "hitl",
    "hitl": true,
    "blockedReason": null
  },
  {
    "id": "C007",
    "test_case": "maturity_high",
    "板块": "B",
    "合同类型": "投资合作类",
    "金额": 5000000,
    "关联项目id": "P004",
    "发起人": "陈刚",
    "对方状态": "正常",
    "条款标记": {
      "不可逆": false,
      "担保": false,
      "跨业务": false
    },
    "合同成熟度": "high",
    "说明": "B板块投资合作，高成熟度，走高效审批链",
    "hasTrace": true,
    "outcome": "auto_approved",
    "category": "approved",
    "hitl": false,
    "blockedReason": null
  },
  {
    "id": "C008",
    "test_case": "maturity_low",
    "板块": "B",
    "合同类型": "投资合作类",
    "金额": 5000000,
    "关联项目id": "P004",
    "发起人": "刘洋",
    "对方状态": "正常",
    "条款标记": {
      "不可逆": false,
      "担保": false,
      "跨业务": false
    },
    "合同成熟度": "low",
    "说明": "B板块投资合作，低成熟度，走审慎审批链并触发HITL",
    "hasTrace": true,
    "outcome": "approved",
    "category": "hitl",
    "hitl": true,
    "blockedReason": null
  },
  {
    "id": "C009",
    "test_case": "budget_exceeded",
    "板块": "B",
    "合同类型": "工程类",
    "金额": 10000000,
    "关联项目id": "P004",
    "发起人": "吴敏",
    "对方状态": "正常",
    "条款标记": {
      "不可逆": false,
      "担保": false,
      "跨业务": false
    },
    "说明": "B板块工程合同，项目已评审但合同金额超预算上限",
    "hasTrace": true,
    "outcome": "blocked",
    "category": "blocked",
    "hitl": false,
    "blockedReason": "超预算上限"
  },
  {
    "id": "C010",
    "test_case": "related_party_hitl",
    "板块": "A",
    "合同类型": "采购类",
    "金额": 300000,
    "关联项目id": "P001",
    "发起人": "郑华",
    "对方状态": "正常",
    "条款标记": {
      "不可逆": false,
      "担保": false,
      "跨业务": false
    },
    "关联方标记": true,
    "说明": "A板块采购合同，相对方为集团内B板块关联公司，触发关联交易HITL",
    "hasTrace": true,
    "outcome": "approved",
    "category": "hitl",
    "hitl": true,
    "blockedReason": null
  },
  {
    "id": "C011",
    "test_case": "blacklist_block",
    "板块": "A",
    "合同类型": "采购类",
    "金额": 400000,
    "关联项目id": "P001",
    "发起人": "马琳",
    "对方状态": "黑名单",
    "条款标记": {
      "不可逆": false,
      "担保": false,
      "跨业务": false
    },
    "说明": "相对方在黑名单，counterparty_guard 应拦截",
    "hasTrace": true,
    "outcome": "blocked",
    "category": "blocked",
    "hitl": false,
    "blockedReason": "阻断: 黑名单"
  },
  {
    "id": "C012",
    "test_case": "llm_clause_clear",
    "板块": "A",
    "合同类型": "采购类",
    "金额": 500000,
    "关联项目id": "P001",
    "发起人": "黄蕾",
    "对方状态": "正常",
    "条款标记": {},
    "条款描述": "本合同包含不可撤销的付款承诺，合同金额50万元，相对方为外部供应商，无担保条款，不涉及跨板块业务。",
    "说明": "条款清楚，LLM 应高置信度抽取",
    "hasTrace": false,
    "outcome": null,
    "category": null,
    "hitl": false,
    "blockedReason": null
  },
  {
    "id": "C013",
    "test_case": "llm_clause_ambiguous",
    "板块": "B",
    "合同类型": "服务类",
    "金额": 800000,
    "关联项目id": "P003",
    "发起人": "田野",
    "对方状态": "正常",
    "条款标记": {},
    "条款描述": "本合同涉及一些技术服务安排，可能涉及集团内部公司之间的合作，具体条款尚待确认。",
    "说明": "条款模糊，LLM 应低置信度，触发 HITL",
    "hasTrace": false,
    "outcome": null,
    "category": null,
    "hitl": false,
    "blockedReason": null
  },
  {
    "id": "C014",
    "test_case": "llm_clause_blacklist",
    "板块": "A",
    "合同类型": "采购类",
    "金额": 300000,
    "关联项目id": "P001",
    "发起人": "钱进",
    "对方状态": "正常",
    "条款标记": {},
    "条款描述": "本合同相对方已被列入集团黑名单，存在严重资信不良记录，合同涉及标准设备采购。",
    "说明": "LLM 应识别出黑名单相对方，触发 counterparty_guard 拦截",
    "hasTrace": false,
    "outcome": null,
    "category": null,
    "hitl": false,
    "blockedReason": null
  }
];
const TRACE = {
  "C001": [
    {
      "node": "triage",
      "action": "classify",
      "input_summary": "合同 C001: A-采购类",
      "output_summary": "板块=A, 类型=采购类, 方法=rule",
      "decision": "classified",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "clause_extraction",
      "action": "skip",
      "input_summary": "条款描述为空，跳过 LLM 抽取",
      "output_summary": "沿用已有标记",
      "decision": "skipped",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "rag",
      "action": "retrieve_sop",
      "input_summary": "合同类型: 采购类",
      "output_summary": "SOP 已检索",
      "decision": "found",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "route",
      "action": "lookup_approval_chain",
      "input_summary": "A-采购类, ¥300,000",
      "output_summary": "审批链: 部门负责人 → 财务负责人 → 分管副总",
      "decision": "routed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_counterparty",
      "input_summary": "对方状态: 正常",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_project",
      "input_summary": "项目ID: P001",
      "output_summary": "项目已通过，预算合规",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_isolation",
      "input_summary": "跨业务标记: False",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "hitl",
      "action": "auto_approve",
      "input_summary": "无需人工确认",
      "output_summary": "自动通过",
      "decision": "auto_approved",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    }
  ],
  "C002": [
    {
      "node": "triage",
      "action": "classify",
      "input_summary": "合同 C002: A-采购类",
      "output_summary": "板块=A, 类型=采购类, 方法=rule",
      "decision": "classified",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "clause_extraction",
      "action": "skip",
      "input_summary": "条款描述为空，跳过 LLM 抽取",
      "output_summary": "沿用已有标记",
      "decision": "skipped",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "rag",
      "action": "retrieve_sop",
      "input_summary": "合同类型: 采购类",
      "output_summary": "SOP 已检索",
      "decision": "found",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "route",
      "action": "lookup_approval_chain",
      "input_summary": "A-采购类, ¥6,000,000",
      "output_summary": "审批链: 部门负责人 → 财务负责人 → 分管副总 → 总经理 → 上级",
      "decision": "routed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_counterparty",
      "input_summary": "对方状态: 正常",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_project",
      "input_summary": "项目ID: P002",
      "output_summary": "项目已通过，预算合规",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_isolation",
      "input_summary": "跨业务标记: False",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "hitl",
      "action": "human_review",
      "input_summary": "需人工确认: 金额 ¥6,000,000 超过自动审批阈值",
      "output_summary": "人工决策: approved",
      "decision": "approved",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    }
  ],
  "C003": [
    {
      "node": "triage",
      "action": "classify",
      "input_summary": "合同 C003: B-工程类",
      "output_summary": "板块=B, 类型=工程类, 方法=rule",
      "decision": "classified",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "clause_extraction",
      "action": "skip",
      "input_summary": "条款描述为空，跳过 LLM 抽取",
      "output_summary": "沿用已有标记",
      "decision": "skipped",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "rag",
      "action": "retrieve_sop",
      "input_summary": "合同类型: 工程类",
      "output_summary": "SOP 已检索",
      "decision": "found",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "route",
      "action": "lookup_approval_chain",
      "input_summary": "B-工程类, ¥3,000,000",
      "output_summary": "审批链: 项目负责人 → 财务负责人 → 分管副总",
      "decision": "routed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_counterparty",
      "input_summary": "对方状态: 正常",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_project",
      "input_summary": "项目ID: P_NOT_APPROVED",
      "output_summary": "项目未通过",
      "decision": "blocked",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    }
  ],
  "C004": [
    {
      "node": "triage",
      "action": "classify",
      "input_summary": "合同 C004: B-服务类",
      "output_summary": "板块=B, 类型=服务类, 方法=rule",
      "decision": "classified",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "clause_extraction",
      "action": "skip",
      "input_summary": "条款描述为空，跳过 LLM 抽取",
      "output_summary": "沿用已有标记",
      "decision": "skipped",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "rag",
      "action": "retrieve_sop",
      "input_summary": "合同类型: 服务类",
      "output_summary": "SOP 已检索",
      "decision": "found",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "route",
      "action": "lookup_approval_chain",
      "input_summary": "B-服务类, ¥2,000,000",
      "output_summary": "审批链: 项目负责人 → 总经理 → 上级",
      "decision": "routed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_counterparty",
      "input_summary": "对方状态: 正常",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_project",
      "input_summary": "项目ID: P003",
      "output_summary": "项目已通过，预算合规",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_isolation",
      "input_summary": "跨业务标记: True",
      "output_summary": "阻断: 需合规审查",
      "decision": "blocked",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    }
  ],
  "C005": [
    {
      "node": "triage",
      "action": "classify",
      "input_summary": "合同 C005: C-服务类",
      "output_summary": "板块=C, 类型=服务类, 方法=rule",
      "decision": "classified",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "clause_extraction",
      "action": "skip",
      "input_summary": "条款描述为空，跳过 LLM 抽取",
      "output_summary": "沿用已有标记",
      "decision": "skipped",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "rag",
      "action": "retrieve_sop",
      "input_summary": "合同类型: 服务类",
      "output_summary": "SOP 已检索",
      "decision": "found",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "route",
      "action": "lookup_approval_chain",
      "input_summary": "C-服务类, ¥200,000",
      "output_summary": "审批链: 业务经办 → 部门负责人 → 分管副总",
      "decision": "routed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_counterparty",
      "input_summary": "对方状态: 正常",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_project",
      "input_summary": "项目ID: None",
      "output_summary": "项目已通过，预算合规",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_isolation",
      "input_summary": "跨业务标记: False",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "hitl",
      "action": "auto_approve",
      "input_summary": "无需人工确认",
      "output_summary": "自动通过",
      "decision": "auto_approved",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    }
  ],
  "C006": [
    {
      "node": "triage",
      "action": "classify",
      "input_summary": "合同 C006: D-担保类",
      "output_summary": "板块=D, 类型=担保类, 方法=rule",
      "decision": "classified",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "clause_extraction",
      "action": "skip",
      "input_summary": "条款描述为空，跳过 LLM 抽取",
      "output_summary": "沿用已有标记",
      "decision": "skipped",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "rag",
      "action": "retrieve_sop",
      "input_summary": "合同类型: 担保类",
      "output_summary": "SOP 已检索",
      "decision": "found",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "route",
      "action": "lookup_approval_chain",
      "input_summary": "D-担保类, ¥1,000,000",
      "output_summary": "审批链: 财务负责人 → 法务负责人 → 上级",
      "decision": "routed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_counterparty",
      "input_summary": "对方状态: 正常",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_project",
      "input_summary": "项目ID: None",
      "output_summary": "项目已通过，预算合规",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_isolation",
      "input_summary": "跨业务标记: False",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "hitl",
      "action": "human_review",
      "input_summary": "需人工确认: 金额 ¥1,000,000 超过自动审批阈值; 包含担保条款",
      "output_summary": "人工决策: approved",
      "decision": "approved",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    }
  ],
  "C007": [
    {
      "node": "triage",
      "action": "classify",
      "input_summary": "合同 C007: B-投资合作类",
      "output_summary": "板块=B, 类型=投资合作类, 方法=rule",
      "decision": "classified",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "clause_extraction",
      "action": "skip",
      "input_summary": "条款描述为空，跳过 LLM 抽取",
      "output_summary": "沿用已有标记",
      "decision": "skipped",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "rag",
      "action": "retrieve_sop",
      "input_summary": "合同类型: 投资合作类",
      "output_summary": "SOP 未找到",
      "decision": "missing",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "route",
      "action": "lookup_approval_chain",
      "input_summary": "B-投资合作类, ¥5,000,000",
      "output_summary": "审批链: 投资板块负责人 → 财务负责人 → 分管副总",
      "decision": "routed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_counterparty",
      "input_summary": "对方状态: 正常",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_project",
      "input_summary": "项目ID: P004",
      "output_summary": "项目已通过，预算合规",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_isolation",
      "input_summary": "跨业务标记: False",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "hitl",
      "action": "auto_approve",
      "input_summary": "无需人工确认",
      "output_summary": "自动通过",
      "decision": "auto_approved",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    }
  ],
  "C008": [
    {
      "node": "triage",
      "action": "classify",
      "input_summary": "合同 C008: B-投资合作类",
      "output_summary": "板块=B, 类型=投资合作类, 方法=rule",
      "decision": "classified",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "clause_extraction",
      "action": "skip",
      "input_summary": "条款描述为空，跳过 LLM 抽取",
      "output_summary": "沿用已有标记",
      "decision": "skipped",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "rag",
      "action": "retrieve_sop",
      "input_summary": "合同类型: 投资合作类",
      "output_summary": "SOP 未找到",
      "decision": "missing",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "route",
      "action": "lookup_approval_chain",
      "input_summary": "B-投资合作类, ¥5,000,000",
      "output_summary": "审批链: 投资板块负责人 → 总经理 → 上级",
      "decision": "routed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_counterparty",
      "input_summary": "对方状态: 正常",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_project",
      "input_summary": "项目ID: P004",
      "output_summary": "项目已通过，预算合规",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_isolation",
      "input_summary": "跨业务标记: False",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "hitl",
      "action": "human_review",
      "input_summary": "需人工确认: 金额 ¥5,000,000 超过自动审批阈值",
      "output_summary": "人工决策: approved",
      "decision": "approved",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    }
  ],
  "C009": [
    {
      "node": "triage",
      "action": "classify",
      "input_summary": "合同 C009: B-工程类",
      "output_summary": "板块=B, 类型=工程类, 方法=rule",
      "decision": "classified",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "clause_extraction",
      "action": "skip",
      "input_summary": "条款描述为空，跳过 LLM 抽取",
      "output_summary": "沿用已有标记",
      "decision": "skipped",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "rag",
      "action": "retrieve_sop",
      "input_summary": "合同类型: 工程类",
      "output_summary": "SOP 已检索",
      "decision": "found",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "route",
      "action": "lookup_approval_chain",
      "input_summary": "B-工程类, ¥10,000,000",
      "output_summary": "审批链: 项目负责人 → 财务负责人 → 分管副总",
      "decision": "routed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_counterparty",
      "input_summary": "对方状态: 正常",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_project_budget",
      "input_summary": "项目ID: P004, 合同金额: ¥10,000,000, 预算上限: ¥8,000,000",
      "output_summary": "超预算上限",
      "decision": "blocked",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    }
  ],
  "C010": [
    {
      "node": "triage",
      "action": "classify",
      "input_summary": "合同 C010: A-采购类",
      "output_summary": "板块=A, 类型=采购类, 方法=rule",
      "decision": "classified",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "clause_extraction",
      "action": "skip",
      "input_summary": "条款描述为空，跳过 LLM 抽取",
      "output_summary": "沿用已有标记",
      "decision": "skipped",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "rag",
      "action": "retrieve_sop",
      "input_summary": "合同类型: 采购类",
      "output_summary": "SOP 已检索",
      "decision": "found",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "route",
      "action": "lookup_approval_chain",
      "input_summary": "A-采购类, ¥300,000",
      "output_summary": "审批链: 部门负责人 → 财务负责人 → 分管副总",
      "decision": "routed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_counterparty",
      "input_summary": "对方状态: 正常",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_project",
      "input_summary": "项目ID: P001",
      "output_summary": "项目已通过，预算合规",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_isolation",
      "input_summary": "跨业务标记: False",
      "output_summary": "通过",
      "decision": "passed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "hitl",
      "action": "human_review",
      "input_summary": "需人工确认: 关联交易需增强审查（法务+财务会签）",
      "output_summary": "人工决策: approved",
      "decision": "approved",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    }
  ],
  "C011": [
    {
      "node": "triage",
      "action": "classify",
      "input_summary": "合同 C011: A-采购类",
      "output_summary": "板块=A, 类型=采购类, 方法=rule",
      "decision": "classified",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "clause_extraction",
      "action": "skip",
      "input_summary": "条款描述为空，跳过 LLM 抽取",
      "output_summary": "沿用已有标记",
      "decision": "skipped",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "rag",
      "action": "retrieve_sop",
      "input_summary": "合同类型: 采购类",
      "output_summary": "SOP 已检索",
      "decision": "found",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "route",
      "action": "lookup_approval_chain",
      "input_summary": "A-采购类, ¥400,000",
      "output_summary": "审批链: 部门负责人 → 财务负责人 → 分管副总",
      "decision": "routed",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    {
      "node": "guardrail",
      "action": "check_counterparty",
      "input_summary": "对方状态: 黑名单",
      "output_summary": "阻断: 黑名单",
      "decision": "blocked",
      "duration_ms": 1,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    }
  ]
};
