"""Generate minimal synthetic data for demo — 4 scenarios only.

All data is FICTIONAL. Board names (A-D), contract types, person names,
and org structures are invented for demonstration purposes. No real
business logic or enterprise architecture is represented.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def build_approval_matrix():
    """Minimal approval matrix — only entries needed for 4 demo scenarios."""
    return [
        # --- 场景 1: 正常审批 ---
        {
            "板块": "A",
            "板块标记": "受监管",
            "合同类型": "采购类",
            "金额上限": 500000,
            "审批链": ["部门负责人", "财务负责人", "分管副总"],
            "需人工确认": False,
        },
        {
            "板块": "A",
            "板块标记": "受监管",
            "合同类型": "服务类",
            "金额上限": 500000,
            "审批链": ["业务经办", "部门负责人", "分管副总"],
            "需人工确认": False,
        },
        # --- 场景 2: 大额 HITL ---
        {
            "板块": "A",
            "板块标记": "受监管",
            "合同类型": "采购类",
            "金额上限": 999999999,
            "审批链": ["部门负责人", "财务负责人", "分管副总", "总经理", "上级"],
            "需人工确认": True,
        },
        {
            "板块": "B",
            "板块标记": "",
            "合同类型": "服务类",
            "金额上限": 999999999,
            "审批链": ["项目负责人", "总经理", "上级"],
            "需人工确认": True,
        },
        {
            "板块": "D",
            "板块标记": "",
            "合同类型": "担保类",
            "金额上限": 999999999,
            "审批链": ["财务负责人", "法务负责人", "上级"],
            "需人工确认": True,
        },
        # --- 场景 3 & 4: guardrail 阻断 ---
        {
            "板块": "B",
            "板块标记": "",
            "合同类型": "工程类",
            "金额上限": 999999999,
            "审批链": ["项目负责人", "财务负责人", "分管副总"],
            "需人工确认": False,
        },
        {
            "板块": "B",
            "板块标记": "",
            "合同类型": "服务类",
            "金额上限": 999999999,
            "审批链": ["项目负责人", "总经理", "上级"],
            "需人工确认": False,
        },
        {
            "板块": "C",
            "板块标记": "竞争性",
            "合同类型": "服务类",
            "金额上限": 999999999,
            "审批链": ["业务经办", "部门负责人", "分管副总"],
            "需人工确认": False,
        },
    ]


def build_templates():
    """Minimal SOP templates for demo."""
    return {
        "采购类": """# 采购类合同 审批SOP
## 流程
1. 部门负责人确认采购需求
2. 财务负责人审核预算
3. 分管副总批准
## 注意事项
- 大额采购需总经理和上级审批
- 必须关联已立项的项目
""",
        "工程类": """# 工程类合同 审批SOP
## 流程
1. 项目负责人确认工程需求
2. 财务负责人审核预算
3. 分管副总批准
## 注意事项
- 关联项目必须通过评审
- 跨板块工程需额外合规审查
""",
        "担保类": """# 担保类合同 审批SOP
## 流程
1. 财务负责人确认融资需求
2. 法务负责人审查担保条款
3. 上级批准
## 注意事项
- 担保合同为高风险类型，必须人工确认
- 需关联主合同
""",
    }


def build_contracts(matrix):
    """4 demo contracts — one per scenario."""
    return [
        # Case 1: 正常审批
        {
            "id": "C001",
            "test_case": "normal_routing",
            "板块": "A",
            "合同类型": "采购类",
            "金额": 300000,
            "关联项目id": "P001",
            "发起人": "张明",
            "条款标记": {"不可逆": False, "担保": False, "跨业务": False},
            "说明": "标准采购，金额适中，项目已立项",
        },
        # Case 2: 大额 → HITL
        {
            "id": "C002",
            "test_case": "amount_hitl",
            "板块": "A",
            "合同类型": "采购类",
            "金额": 6000000,
            "关联项目id": "P002",
            "发起人": "李芳",
            "条款标记": {"不可逆": False, "担保": False, "跨业务": False},
            "说明": "大额采购，需人工确认",
        },
        # Case 3: 项目未评审 → guardrail 阻断
        {
            "id": "C003",
            "test_case": "project_block",
            "板块": "B",
            "合同类型": "工程类",
            "金额": 3000000,
            "关联项目id": "P_NOT_APPROVED",
            "发起人": "王强",
            "条款标记": {"不可逆": False, "担保": False, "跨业务": False},
            "说明": "工程合同，关联项目未通过评审",
        },
        # Case 4: 跨板块 → guardrail 阻断
        {
            "id": "C004",
            "test_case": "isolation_block",
            "板块": "B",
            "合同类型": "服务类",
            "金额": 2000000,
            "关联项目id": "P003",
            "发起人": "赵伟",
            "条款标记": {"不可逆": False, "担保": False, "跨业务": True},
            "说明": "跨板块服务合同，需隔离审查",
        },
    ]


def build_projects():
    """Minimal project ledger."""
    return [
        {"项目id": "P001", "已评审通过": True, "板块": "A", "项目名称": "设备更新项目"},
        {"项目id": "P002", "已评审通过": True, "板块": "A", "项目名称": "大型采购项目"},
        {"项目id": "P003", "已评审通过": True, "板块": "B", "项目名称": "投资项目"},
        {"项目id": "P_NOT_APPROVED", "已评审通过": False, "板块": "B", "项目名称": "（未通过评审）"},
    ]


def main():
    matrix = build_approval_matrix()
    templates = build_templates()
    contracts = build_contracts(matrix)
    projects = build_projects()

    with open(DATA_DIR / "approval_matrix.json", "w", encoding="utf-8") as f:
        json.dump(matrix, f, ensure_ascii=False, indent=2)
    print(f"[OK] approval_matrix.json — {len(matrix)} entries")

    with open(DATA_DIR / "contracts.jsonl", "w", encoding="utf-8") as f:
        for c in contracts:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"[OK] contracts.jsonl — {len(contracts)} contracts")

    with open(DATA_DIR / "projects.jsonl", "w", encoding="utf-8") as f:
        for p in projects:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"[OK] projects.jsonl — {len(projects)} projects")

    tpl_dir = DATA_DIR / "templates"
    tpl_dir.mkdir(exist_ok=True)
    for name, content in templates.items():
        with open(tpl_dir / f"{name}.md", "w", encoding="utf-8") as f:
            f.write(content)
    print(f"[OK] templates/ — {len(templates)} templates")

    print(f"\nScenario coverage:")
    for c in contracts:
        print(f"  {c['id']} | {c['test_case']:15s} | {c['说明']}")


if __name__ == "__main__":
    main()
