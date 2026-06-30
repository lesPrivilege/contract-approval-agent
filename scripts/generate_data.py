"""Generate minimal synthetic data for demo — 4 scenarios only.

All data is FICTIONAL. Names, org structures, contract types are invented
for demonstration purposes. No real business logic or enterprise architecture
is represented.
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
            "板块": "燃气",
            "合同类型": "设备采购",
            "金额上限": 500000,
            "审批链": ["部门主管", "财务经理", "分公司总经理"],
            "需人工确认": False,
        },
        {
            "板块": "燃气",
            "合同类型": "供气设施安装",
            "金额上限": 500000,
            "审批链": ["业务经办", "部门主管", "分公司总经理"],
            "需人工确认": False,
        },
        # --- 场景 2: 大额 HITL ---
        {
            "板块": "燃气",
            "合同类型": "设备采购",
            "金额上限": float("inf"),
            "审批链": ["部门主管", "财务经理", "分公司总经理", "区域总监", "集团副总裁"],
            "需人工确认": True,
        },
        {
            "板块": "综合能源",
            "合同类型": "运营维保",
            "金额上限": float("inf"),
            "审批链": ["项目负责人", "区域总监", "集团副总裁"],
            "需人工确认": True,
        },
        {
            "板块": "行政",
            "合同类型": "借款担保",
            "金额上限": float("inf"),
            "审批链": ["财务经理", "法务经理", "集团副总裁"],
            "需人工确认": True,
        },
        # --- 场景 3 & 4: guardrail 阻断（不走审批链，但矩阵里需要有定义） ---
        {
            "板块": "综合能源",
            "合同类型": "工程施工",
            "金额上限": float("inf"),
            "审批链": ["项目负责人", "财务经理", "分公司总经理"],
            "需人工确认": False,
        },
        {
            "板块": "综合能源",
            "合同类型": "能源管理",
            "金额上限": float("inf"),
            "审批链": ["项目负责人", "区域总监", "集团副总裁"],
            "需人工确认": False,
        },
        {
            "板块": "智慧家居",
            "合同类型": "社区服务",
            "金额上限": float("inf"),
            "审批链": ["业务经办", "部门主管", "分公司总经理"],
            "需人工确认": False,
        },
    ]


def build_templates():
    """Minimal SOP templates for demo."""
    return {
        "设备采购": """# 设备采购合同 审批SOP
## 流程
1. 部门主管确认采购需求
2. 财务经理审核预算
3. 分公司总经理批准
## 注意事项
- 大额采购（>50万）需区域总监和集团副总裁审批
- 必须关联已立项的项目
""",
        "工程施工": """# 工程施工合同 审批SOP
## 流程
1. 项目负责人确认工程需求
2. 财务经理审核预算
3. 分公司总经理批准
## 注意事项
- 关联项目必须通过投资评审
- 跨区域工程需额外合规审查
""",
        "借款担保": """# 借款担保合同 审批SOP
## 流程
1. 财务经理确认融资需求
2. 法务经理审查担保条款
3. 集团副总裁批准
## 注意事项
- 担保合同为高风险类型，必须人工确认
- 需关联主借款合同
""",
    }


def build_contracts(matrix):
    """4 demo contracts — one per scenario."""
    return [
        # Case 1: 正常审批
        {
            "id": "C001",
            "test_case": "normal_routing",
            "板块": "燃气",
            "合同类型": "设备采购",
            "金额": 300000,
            "关联项目id": "P001",
            "发起人": "张明",
            "条款标记": {"不可逆": False, "担保": False, "跨业务": False},
            "说明": "标准设备采购，金额适中，项目已立项",
        },
        # Case 2: 大额 → HITL
        {
            "id": "C002",
            "test_case": "amount_hitl",
            "板块": "燃气",
            "合同类型": "设备采购",
            "金额": 6000000,
            "关联项目id": "P002",
            "发起人": "李芳",
            "条款标记": {"不可逆": False, "担保": False, "跨业务": False},
            "说明": "大额设备采购，需人工确认",
        },
        # Case 3: 项目未立项 → guardrail 阻断
        {
            "id": "C003",
            "test_case": "project_block",
            "板块": "综合能源",
            "合同类型": "工程施工",
            "金额": 3000000,
            "关联项目id": "P_NOT_APPROVED",
            "发起人": "王强",
            "条款标记": {"不可逆": False, "担保": False, "跨业务": False},
            "说明": "工程施工，关联项目未通过投资评审",
        },
        # Case 4: 跨业务 → guardrail 阻断
        {
            "id": "C004",
            "test_case": "isolation_block",
            "板块": "综合能源",
            "合同类型": "能源管理",
            "金额": 2000000,
            "关联项目id": "P003",
            "发起人": "赵伟",
            "条款标记": {"不可逆": False, "担保": False, "跨业务": True},
            "说明": "能源管理合同涉及受监管区域，需隔离审查",
        },
    ]


def build_projects():
    """Minimal project ledger."""
    return [
        {"项目id": "P001", "已评审通过": True, "板块": "燃气", "项目名称": "设备更新项目"},
        {"项目id": "P002", "已评审通过": True, "板块": "燃气", "项目名称": "大型采购项目"},
        {"项目id": "P003", "已评审通过": True, "板块": "综合能源", "项目名称": "光伏投资项目"},
        {"项目id": "P_NOT_APPROVED", "已评审通过": False, "板块": "综合能源", "项目名称": "（未通过评审）"},
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
