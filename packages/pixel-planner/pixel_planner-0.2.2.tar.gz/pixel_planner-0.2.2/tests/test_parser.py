from scripts.pixel_planner import parse_markdown_for_phases


def test_parse_phases_without_week_and_with_assignee():
    md = """
## Phase 01 – Sample

| **Milestone** | **Description** | Status | Baseline Plan | Current Plan | Assignee | Comments |
| ------------- | ---------------- | ------ | ------------- | ------------ | -------- | -------- |
| A             | a                | Done   | 2025-01-01    | 2025-01-02   | user     | note     |

---
""".strip()

    phases = parse_markdown_for_phases(md)
    assert len(phases) == 1
    p = phases[0]
    assert p.name == "Sample"
    assert len(p.milestones) == 1
    m = p.milestones[0]
    assert m.status.lower() == "done"
    assert m.baseline_plan is not None and m.current_plan is not None

