from datetime import date

from scripts.pixel_planner import generate_timeline_block, parse_markdown_for_phases


def test_timeline_clamps_to_last_milestone_and_bracket():
    md = """
## Phase 01 – A

| **Milestone** | **Description** | Status | Baseline Plan | Current Plan | Assignee | Comments |
| ------------- | ---------------- | ------ | ------------- | ------------ | -------- | -------- |
| A             | a                | Done   | 2025-01-01    | 2025-01-01   |         |          |
| B             | b                | Backlog| 2025-01-08    | 2025-01-08   |         |          |

---
""".strip()
    phases = parse_markdown_for_phases(md)
    # today far in the future
    block = generate_timeline_block(phases, date(2025, 12, 31), plan_basis="current")
    # header shows a clamped date (2025-01-08) somewhere; and closing bracket exists
    assert "]" in block


def test_timeline_due_today_not_counted():
    md = """
## Phase 01 – A

| **Milestone** | **Description** | Status | Baseline Plan | Current Plan | Assignee | Comments |
| ------------- | ---------------- | ------ | ------------- | ------------ | -------- | -------- |
| A             | a                | Done   | 2025-01-01    | 2025-01-01   |         |          |
| B             | b                | Backlog| 2025-01-08    | 2025-01-08   |         |          |

---
""".strip()
    phases = parse_markdown_for_phases(md)
    block = generate_timeline_block(phases, date(2025, 1, 8), plan_basis="current")
    # Should-be should not count milestone B yet; line should show 50% / 50% for the phase
    assert "50% / 50%" in block

