# Pixel Planner

Automate project plans written in Markdown. Generate a clean, gantt-like timeline from your phases and milestones, and keep progress indicators up to date with a single command.

## Features
- Initialize a new plan from a template
- Parse phases and milestones from the plan
- Generate/refresh a gantt-like "Project Timeline (Phases)" section
- Generate/refresh "Milestone Status Overview" graph showing status distribution
- Current-date marker with clamping to last milestone date
- Global and per-phase percentages showing actual vs should-be
- Flexible baseline vs current planning basis selection for timeline comparison

## Installation

### Option 1: Install via pip (Recommended)
```bash
pip install pixel-planner
```

### Option 2: Clone and run (Development)
- Python 3.9+ required
- Clone this repository and use `python3 scripts/pixel_planner.py`

## Quick start
1) Create a plan from the template

```bash
# If installed via pip/brew:
pixel-planner init --out Project-Plan.md --project "My Project"

# If using cloned repository:
python3 scripts/pixel_planner.py init \
  --template templates/pixel-planner-phase-template.md \
  --out Project-Plan.md \
  --project "My Project"
```

2) Edit your plan: fill the phases and milestone tables

3) Generate or refresh the timeline

- In place (recommended):
```bash
# If installed via pip/brew:
pixel-planner timeline --in Project-Plan.md --in-place --basis current

# If using cloned repository:
python3 scripts/pixel_planner.py timeline --in Project-Plan.md --in-place --basis current
```

- Include milestone status overview graph:
```bash
pixel-planner timeline --in Project-Plan.md --in-place --basis current --include-status
```

- To a separate file using baseline dates:
```bash
pixel-planner timeline --in Project-Plan.md --out Project-Plan.out.md --basis baseline --version v1.0
```

- Generate as-of a specific date (for reproducible timelines):
```bash
pixel-planner timeline --in Project-Plan.md --in-place --basis current --date 2025-03-02
```

## Sample project
- A complete example is included: [`Sample-Project-Plan.md`](./Sample-Project-Plan.md)
- Regenerate its timeline anytime:

```bash
# If installed via pip/brew:
pixel-planner timeline --in Sample-Project-Plan.md --in-place --basis current --include-status

# If using cloned repository:
python3 scripts/pixel_planner.py timeline --in Sample-Project-Plan.md --in-place --basis current --include-status
```

## Short history (vibe-coding)
- This project was built using a vibe-coding (AI-assisted pair programming) workflow.
- The only manually created artifact at the start was the first Markdown template; everything else
  (the Python CLI, timeline logic, clamping and percentage rules, sample plan, tests, CI, and repo docs)
  was iteratively generated and refined in-session.

My take: this approach fits this tool very well. Rapid, iterative edits plus immediate feedback make it
easy to converge on the exact timeline semantics and formatting you want. The added tests and CI balance
speed with correctness and maintainability. For larger systems, I’d complement this with brief design docs
and peer reviews, but for a focused automation like Pixel Planner, vibe-coding was a strong choice.

## Template rules (what the script expects)
- Timeline section
  - There must be a heading named exactly `## Project Timeline (Phases)`
  - The content under it is a fenced block (```text ... ```). The script fully rewrites this block.

- Phase sections
  - Each phase must use a heading of the form: `## Phase 01 – Phase Name` (hyphen `-` also accepted instead of the en dash `–`).

- Milestone table under each phase
  - Columns (any alignment/width). Names are matched case-insensitively by meaning:
    - Milestone | Description | Status | Baseline Plan | Current Plan | Assignee | Comments
  - Dates must be ISO `YYYY-MM-DD`. Values like `N/A`, `NA`, `TBD` are treated as empty.
  - A milestone is counted as executed only when `Status` is `Done` (case-insensitive).

## Timeline details
- Bars and weeks
  - Each `■` represents one calendar week. Bars are aligned over a global week grid spanning the earliest to latest plan dates (based on `--basis`).
  - A vertical `|` marks the effective date week.
  - Bars always close with a `]` and are clipped properly at the right edge.

- Effective date (header arrow)
  - The header shows: `┌─→ YYYY-MM-DD (X% / Y%)`
  - The effective date is today, but if today is beyond the last milestone date (across all phases), it is clamped to that last milestone date.

- Basis (which plan dates are used)
  - `--basis current` (default): position bars and compute "should-be" from Current Plan dates. Shows activity evolution percentages.
  - `--basis baseline`: use Baseline Plan dates instead. Shows clean timeline bars without activity evolution percentages.
  - This separation allows you to maintain both your original baseline and revised current plans, enabling comparison between planned vs actual timeline evolution.
  - You can generate timelines using either version independently, making it easy to track scope changes and schedule adjustments over time.

## Percentages (progress logic)
**Note: Activity evolution percentages are only shown for `--basis current` timelines. Baseline timelines show clean bars without percentages.**

- Header percentages (global): `X% / Y%`
  - X% = executed/total across all milestones (executed = count of `Done`).
  - Y% = planned-by-effective-date/total across all milestones, based on the chosen basis.

- Per-phase percentages: `X% / Y%`
  - X% = executed_in_phase / total_in_phase.
  - Y% = planned_by_effective_date_in_phase / total_in_phase, using the chosen basis.

- Important rule: "planned-by-effective-date" uses a strict comparison of planned date < effective date. Milestones due today are counted as should-be tomorrow (after the day passes).

- Direction indicator: ▲ if executed ≥ should-be; otherwise ▼ (for current timelines only).

## Milestone Status Overview
When using `--include-status`, a status graph is generated showing milestone distribution:

- Each ■ represents 10% of total milestones
- Status names are automatically aligned for readability
- Sorted by count (descending), then alphabetically

```text
- Backlog          : 14 → [■ ■ ■ ■ ■ ■ ■ ■] 82%
- Done             : 01 → [■] 6%
- In Progress      : 01 → [■] 6%
- Ready for Review : 01 → [■] 6%
```

## Example timelines

### Current timeline (with activity evolution percentages)
```vb
                                                              ┌─→ 2025-03-02 (33% / 67%)
- Phase 01 – Install Infrastructure ▲ W 05-08 2025-01-31 to 2025-02-20 → [■ ■ ■ ■] 50% / 100%
- Phase 02 – Deploy new App ▼         W 09-09 2025-03-02 to 2025-03-02 →     |      [■] 0% / 0%
```

### Baseline timeline (clean bars without percentages)
```text
- Phase 01 – Install Infrastructure ▲ W 05-08 2025-01-31 to 2025-02-20 → [■ ■ ■ ■]
- Phase 02 – Deploy new App ▲         W 09-09 2025-03-02 to 2025-03-02 →         [■]
```

## Tips and gotchas
- Keep the timeline heading spelled exactly as `## Project Timeline (Phases)`
- Keep the status heading spelled exactly as `## Milestone Status Overview` (when using `--include-status`)
- Use correct phase heading format: `## Phase <number> – <name>` (or `-`)
- Use ISO dates. If a phase has no valid dates for the selected basis, its bar may be empty but the line still renders.
- Only `Done` marks a milestone as executed.
- The `Week` column is deprecated and ignored in parsing; you can safely remove it.

## Troubleshooting
- Timeline didn't update
  - Check the heading and code fence (```text) under the timeline section
- Status overview didn't update
  - Check the heading and code fence (```text) under the status section
  - Ensure you used `--include-status` flag
- A phase didn't show a bar
  - Ensure it has at least one valid planned date for the chosen basis
- Percentages look wrong
  - Verify `Status` values and planned dates; items due today don't count as should-be yet

## Development & Contributing

### Development Setup
```bash
git clone https://github.com/ivannagy/pixel-planner.git
cd pixel-planner
pip install -r requirements-dev.txt
pip install -e .
```

### Running Tests
```bash
pytest -q              # Run all tests
ruff check .           # Lint code
mypy pixel_planner     # Type check
```

### Releasing
See [RELEASING.md](RELEASING.md) for the automated release process.

### Contributing
Improvements welcome! Please:
- Keep changes small and readable
- Add tests for new functionality
- Follow existing code style
- Submit pull requests for review

## License
Apache-2.0. See `LICENSE`. A `NOTICE` file is included for attribution.
