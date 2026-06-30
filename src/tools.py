"""Tools — mock business system functions."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

_approval_matrix: list[dict] | None = None
_projects: dict[str, dict] | None = None
_templates: dict[str, str] | None = None


def _load_approval_matrix() -> list[dict]:
    global _approval_matrix
    if _approval_matrix is None:
        with open(DATA_DIR / "approval_matrix.json", encoding="utf-8") as f:
            _approval_matrix = json.load(f)
    return _approval_matrix


def _load_projects() -> dict[str, dict]:
    global _projects
    if _projects is None:
        _projects = {}
        with open(DATA_DIR / "projects.jsonl", encoding="utf-8") as f:
            for line in f:
                p = json.loads(line)
                _projects[p["项目id"]] = p
    return _projects


def _load_templates() -> dict[str, str]:
    global _templates
    if _templates is None:
        _templates = {}
        tpl_dir = DATA_DIR / "templates"
        for fp in tpl_dir.glob("*.md"):
            _templates[fp.stem] = fp.read_text(encoding="utf-8")
    return _templates


def get_approval_chain(board: str, contract_type: str, amount: int) -> list[str] | None:
    """Look up approval chain from matrix. Returns chain or None if not found."""
    matrix = _load_approval_matrix()
    # Find matching entries, sorted by amount threshold
    candidates = [
        e for e in matrix
        if e["板块"] == board and e["合同类型"] == contract_type
    ]
    if not candidates:
        return None
    # Pick the entry whose amount上限 covers this amount
    for entry in sorted(candidates, key=lambda e: e["金额上限"]):
        if amount <= entry["金额上限"]:
            return entry["审批链"]
    # Fallback: use the highest threshold entry
    return sorted(candidates, key=lambda e: e["金额上限"])[-1]["审批链"]


def check_project_approved(project_id: str | None) -> bool:
    """Check if project has passed investment review. Returns True if no project linked."""
    if project_id is None:
        return True
    projects = _load_projects()
    project = projects.get(project_id)
    if project is None:
        return False
    return project.get("已评审通过", False)


def check_cross_business(contract: dict) -> bool:
    """Check if contract crosses business boundaries."""
    return contract.get("条款标记", {}).get("跨业务", False)


def get_sop(contract_type: str) -> str | None:
    """Retrieve SOP template for a contract type."""
    templates = _load_templates()
    return templates.get(contract_type)


def needs_hitl(board: str, contract_type: str, amount: int) -> bool:
    """Check if contract requires human-in-the-loop approval."""
    matrix = _load_approval_matrix()
    candidates = [
        e for e in matrix
        if e["板块"] == board and e["合同类型"] == contract_type
    ]
    for entry in sorted(candidates, key=lambda e: e["金额上限"]):
        if amount <= entry["金额上限"]:
            return entry.get("需人工确认", False)
    if candidates:
        return sorted(candidates, key=lambda e: e["金额上限"])[-1].get("需人工确认", False)
    return False
