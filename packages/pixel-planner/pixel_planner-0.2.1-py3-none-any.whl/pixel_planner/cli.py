#!/usr/bin/env python3

import argparse
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Sequence

# -----------------------------
# Data models
# -----------------------------


@dataclass
class Milestone:
    milestone: str
    description: str
    status: str
    week_range: Optional[str]
    baseline_plan: Optional[date]
    current_plan: Optional[date]
    comments: Optional[str] = None


@dataclass
class Phase:
    number: str
    name: str
    milestones: List[Milestone] = field(default_factory=list)

    # Derived fields (computed later)
    baseline_start: Optional[date] = None
    baseline_end: Optional[date] = None
    current_start: Optional[date] = None
    current_end: Optional[date] = None


# -----------------------------
# Utilities
# -----------------------------


DATE_FMT = "%Y-%m-%d"


def parse_date(value: str) -> Optional[date]:
    value = value.strip()
    if not value or value.upper() in {"N/A", "NA", "TBD"}:
        return None
    try:
        return datetime.strptime(value, DATE_FMT).date()
    except ValueError:
        return None


def iso_week_number(d: date) -> int:
    return d.isocalendar()[1]


def start_of_week_monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def safe_min(dates: Sequence[Optional[date]]) -> Optional[date]:
    vals = [d for d in dates if d is not None]
    return min(vals) if vals else None


def safe_max(dates: Sequence[Optional[date]]) -> Optional[date]:
    vals = [d for d in dates if d is not None]
    return max(vals) if vals else None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# -----------------------------
# Markdown parsing
# -----------------------------


PHASE_HEADING_RE = re.compile(r"^##\s+Phase\s+(\d+)\s+[–-]\s*(.+)$")


def parse_markdown_for_phases(md: str) -> List[Phase]:
    lines = md.splitlines()
    phases: List[Phase] = []
    i = 0
    current_phase: Optional[Phase] = None

    while i < len(lines):
        line = lines[i].rstrip()
        m = PHASE_HEADING_RE.match(line)
        if m:
            if current_phase:
                phases.append(current_phase)
            current_phase = Phase(number=m.group(1), name=m.group(2))
            i += 1
            # Expect a table after the heading; parse rows until a separator or next heading
            # Skip blank lines
            while i < len(lines) and lines[i].strip() == "":
                i += 1
            # Expect header row starting with '|', capture columns mapping (supports optional 'Week')
            header_cells: List[str] = []
            if i < len(lines) and lines[i].lstrip().startswith("|"):
                raw_header = lines[i]
                header_cells = [c.strip() for c in raw_header.strip().strip("|").split("|")]
                def norm(h: str) -> str:
                    h = re.sub(r"\*", "", h)
                    h = re.sub(r"[^A-Za-z0-9]+", " ", h).strip().lower()
                    return h
                header_map = {norm(h): idx for idx, h in enumerate(header_cells)}
                # Common header names
                # Milestone columns can be named 'milestone'
                def idx_of(*names: str) -> Optional[int]:
                    for name in names:
                        if name in header_map:
                            return header_map[name]
                    return None
                idx_milestone = idx_of("milestone")
                idx_description = idx_of("description")
                idx_status = idx_of("status")
                idx_week = idx_of("week")  # optional
                idx_baseline = idx_of("baseline plan", "baseline")
                idx_current = idx_of("current plan", "current")
                idx_comments = idx_of("comments", "comment")
                i += 1  # move past header
                # Skip separator line if present
                if i < len(lines) and lines[i].lstrip().startswith("|") and set(lines[i].replace("|", "").strip()) <= {"-", " "}:
                    i += 1
            # Parse data rows
            while i < len(lines):
                row = lines[i].rstrip()
                if row.startswith("## ") or row.strip() == "---" or not row.strip():
                    break
                if row.lstrip().startswith("|"):
                    cells = [c.strip() for c in row.strip().strip("|").split("|")]
                    # Safely extract by header indices (support both with or without 'Week')
                    def get(idx: Optional[int]) -> Optional[str]:
                        if idx is None:
                            return None
                        return cells[idx] if idx < len(cells) else None
                    milestone = get(idx_milestone) or ""
                    description = get(idx_description) or ""
                    status = get(idx_status) or ""
                    week = get(idx_week)
                    baseline = parse_date(get(idx_baseline) or "") if idx_baseline is not None else None
                    current = parse_date(get(idx_current) or "") if idx_current is not None else None
                    comments = get(idx_comments)
                    if current_phase is not None and any([milestone, description, status, baseline, current, comments]):
                        current_phase.milestones.append(Milestone(
                            milestone=milestone,
                            description=description,
                            status=status,
                            week_range=week,
                            baseline_plan=baseline,
                            current_plan=current,
                            comments=comments,
                        ))
                i += 1
            continue
        i += 1

    if current_phase:
        phases.append(current_phase)

    # Compute derived fields
    for phase in phases:
        phase.baseline_start = safe_min([m.baseline_plan for m in phase.milestones])
        phase.baseline_end = safe_max([m.baseline_plan for m in phase.milestones])
        phase.current_start = safe_min([m.current_plan for m in phase.milestones])
        phase.current_end = safe_max([m.current_plan for m in phase.milestones])

    return phases


# -----------------------------
# Timeline generation
# -----------------------------


def compute_week_index(anchor_monday: date, d: date) -> int:
    return (start_of_week_monday(d) - anchor_monday).days // 7


def compute_weeks_span(start_d: date, end_d: date) -> int:
    start_m = start_of_week_monday(start_d)
    end_m = start_of_week_monday(end_d)
    return (end_m - start_m).days // 7 + 1


def percentage_time_elapsed(start_d: Optional[date], end_d: Optional[date], today: date) -> Optional[float]:
    if start_d is None or end_d is None:
        return None
    if end_d < start_d:
        return None
    total_days = (end_d - start_d).days
    if total_days == 0:
        return 100.0 if today >= end_d else 0.0
    elapsed_days = (min(max(today, start_d), end_d) - start_d).days
    return max(0.0, min(100.0, (elapsed_days / total_days) * 100.0))


def percentage_actual_completion(milestones: List[Milestone]) -> Optional[float]:
    if not milestones:
        return None
    total = len(milestones)
    done = sum(1 for m in milestones if m.status.strip().lower() == "done")
    return (done / total) * 100.0


def format_week_label(d_start: Optional[date], d_end: Optional[date]) -> str:
    if not d_start or not d_end:
        return "W --/--"
    w1 = iso_week_number(d_start)
    w2 = iso_week_number(d_end)
    return f"W {w1:02d}-{w2:02d}"


def format_date_range(d_start: Optional[date], d_end: Optional[date]) -> str:
    s = d_start.strftime(DATE_FMT) if d_start else "YYYY-MM-DD"
    e = d_end.strftime(DATE_FMT) if d_end else "YYYY-MM-DD"
    return f"{s} to {e}"


def generate_timeline_block(phases: List[Phase], today: date, plan_basis: str = "current") -> str:
    # Choose which plan dates to use for alignment and counts
    def start_of(phase: Phase) -> Optional[date]:
        return phase.current_start if plan_basis == "current" else phase.baseline_start

    def end_of(phase: Phase) -> Optional[date]:
        return phase.current_end if plan_basis == "current" else phase.baseline_end

    valid_ranges = [(start_of(p), end_of(p)) for p in phases if start_of(p) and end_of(p)]
    if not valid_ranges:
        return "No phases with valid dates found. Fill in milestone dates first."

    global_start = safe_min([s for s, _ in valid_ranges])
    global_end = safe_max([e for _, e in valid_ranges])
    assert global_start and global_end

    # Clamp the reference date to the last milestone date if today exceeds it
    all_plan_dates: List[date] = []
    for p in phases:
        for m in p.milestones:
            if m.baseline_plan:
                all_plan_dates.append(m.baseline_plan)
            if m.current_plan:
                all_plan_dates.append(m.current_plan)
    last_milestone_date = safe_max(all_plan_dates) if all_plan_dates else None
    effective_today = min(today, last_milestone_date) if last_milestone_date else today

    anchor = start_of_week_monday(global_start)
    total_weeks = compute_weeks_span(global_start, global_end)

    current_week_index = compute_week_index(anchor, effective_today)
    # Clamp within [0, total_weeks-1] to render inside the viewport
    current_week_index = max(0, min(total_weeks - 1, current_week_index))

    cell_width = 2  # each week cell is 2 characters wide: '■ '
    # Add one extra column so the closing ']' of a bar at the far right is always visible
    total_width = total_weeks * cell_width + 1

    # Left section widths for alignment
    phase_labels = [f"- Phase {p.number} – {p.name}" for p in phases]
    phase_w = max([len(s) for s in phase_labels] + [20])
    week_w = len("W 00-00")
    date_w = len("0000-00-00 to 0000-00-00")

    def left_prefix_text(phase: Phase, s: Optional[date], e: Optional[date], direction: str) -> str:
        left = f"{f'- Phase {phase.number} – {phase.name}':<{phase_w}} {format_week_label(s, e):<{week_w}} {format_date_range(s, e):<{date_w}} {direction} → "
        return left

    # Header line with date arrow aligned over the bar
    # Compute global executed vs planned (as share of total milestones)
    all_milestones: List[Milestone] = [m for p in phases for m in p.milestones]
    total_milestones = len(all_milestones)
    executed_count = sum(1 for m in all_milestones if m.status.strip().lower() == "done")
    # Use strict '<' so items due "today" are not yet counted as should-be-done until the day passes
    # Progress calculation should always use baseline dates regardless of plan_basis
    baseline_planned_by_today = sum(1 for m in all_milestones if m.baseline_plan and m.baseline_plan < effective_today)
    planned_by_today = baseline_planned_by_today
    executed_pct = (executed_count / total_milestones * 100.0) if total_milestones > 0 else 0.0
    planned_pct = (planned_by_today / total_milestones * 100.0) if total_milestones > 0 else 0.0
    header_b = f"{executed_pct:.0f}%"
    header_c = f"{planned_pct:.0f}%"

    # Prefix length equals left columns up to and including the arrow and space
    sample_left_prefix = left_prefix_text(phases[0], start_of(phases[0]), end_of(phases[0]), " ")
    left_prefix_len = len(sample_left_prefix)

    lines: List[str] = []
    today_str = effective_today.strftime(DATE_FMT)
    header = " " * (left_prefix_len + current_week_index * cell_width) + f"┌─→ {today_str} ({header_b} / {header_c})"
    lines.append(header)

    for phase, phase_label in zip(phases, phase_labels):
        s = start_of(phase)
        e = end_of(phase)

        # Build background with spaces
        canvas = [" "] * total_width
        # Place current date marker
        marker_pos = current_week_index * cell_width
        if 0 <= marker_pos < total_width:
            canvas[marker_pos] = "|"

        if s and e:
            # Compute block placement
            start_idx = compute_week_index(anchor, s)
            weeks_len = compute_weeks_span(s, e)
            block = "[" + ("■ " * weeks_len).rstrip() + "]"
            block_start_pos = start_idx * cell_width
            # Ensure canvas can fit block (clip if necessary)
            for j, ch in enumerate(block):
                pos = block_start_pos + j
                if 0 <= pos < total_width:
                    canvas[pos] = ch

        # Put marker last so it remains visible
        if 0 <= marker_pos < total_width:
            canvas[marker_pos] = "|"

        bar = "".join(canvas)

        # Per-phase actual vs should-be (always use baseline for progress tracking)
        phase_total = len(phase.milestones)
        phase_done = sum(1 for m in phase.milestones if m.status.strip().lower() == "done")
        # Progress calculation should always use baseline dates regardless of plan_basis
        phase_planned = sum(
            1
            for m in phase.milestones
            if m.baseline_plan and m.baseline_plan < effective_today
        )

        def pct(n: int, d: int) -> str:
            if d <= 0:
                return "0%"
            return f"{(n / d) * 100.0:.0f}%"

        # Direction: ahead if executed >= should-be for this phase
        direction = "▲" if phase_done >= phase_planned else "▼"

        left_prefix = left_prefix_text(phase, s, e, direction)
        a_str = pct(phase_done, phase_total)
        p_str = pct(phase_planned, phase_total)

        lines.append(f"{left_prefix}{bar} {a_str} / {p_str}")

    return "\n".join(lines)


# -----------------------------
# Markdown rewrite
# -----------------------------


def generate_status_graph(phases: List[Phase]) -> str:
    # Count milestones by status across all phases
    status_counts: Dict[str, int] = {}
    all_milestones = [m for p in phases for m in p.milestones]
    total_milestones = len(all_milestones)
    
    if total_milestones == 0:
        return "No milestones found."
    
    for milestone in all_milestones:
        status = milestone.status.strip()
        if not status:
            status = "No Status"
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Sort by count descending, then by name for consistent output
    sorted_statuses = sorted(status_counts.items(), key=lambda x: (-x[1], x[0]))
    
    # Find the longest status name for alignment
    max_status_length = max(len(status) for status, _ in sorted_statuses)
    
    lines = []
    for status, count in sorted_statuses:
        percentage = (count / total_milestones) * 100.0
        # Each ■ represents 10%, so divide by 10 and round
        bar_count = round(percentage / 10.0)
        bars = "■ " * bar_count if bar_count > 0 else ""
        bars = bars.rstrip()  # Remove trailing space
        
        line = f"- {status:<{max_status_length}} : {count:02d} → [{bars}] {percentage:.0f}%"
        lines.append(line)
    
    return "\n".join(lines)


def replace_status_section(md: str, status_block_content: str) -> str:
    lines = md.splitlines()
    n = len(lines)
    # Locate the status heading
    heading_idx = None
    for idx, line in enumerate(lines):
        if line.strip().lower().startswith("## milestone status"):
            heading_idx = idx
            break
    
    if heading_idx is None:
        # If not found, append at end
        new_block = [
            "## Milestone Status Overview",
            "",
            "```text",
            *status_block_content.splitlines(),
            "```",
        ]
        return (md.rstrip() + "\n\n" + "\n".join(new_block) + "\n")
    
    # Find the end of existing status section: prefer closing code fence, otherwise next heading or EOF
    i = heading_idx + 1
    # Skip blank lines
    while i < n and lines[i].strip() == "":
        i += 1
    # If next is an opening fence, skip until matching closing fence
    if i < n and lines[i].strip().startswith("```"):
        i += 1
        while i < n and not lines[i].strip().startswith("```"):
            i += 1
        if i < n and lines[i].strip().startswith("```"):
            i += 1  # include closing fence
    else:
        # No fence; skip until next heading or EOF
        while i < n and not lines[i].strip().startswith("## "):
            i += 1
    
    # Build new content
    before = lines[:heading_idx]
    new_block = [
        lines[heading_idx],
        "",
        "```text",
        *status_block_content.splitlines(),
        "```",
    ]
    after = lines[i:]
    return "\n".join(before + new_block + after).rstrip() + "\n"


def generate_baseline_block(phases: List[Phase], plan_basis: str = "baseline") -> str:
    # Baseline timeline without date markers or effective date calculations
    # Choose which plan dates to use for alignment
    def start_of(phase: Phase) -> Optional[date]:
        return phase.baseline_start if plan_basis == "baseline" else phase.current_start

    def end_of(phase: Phase) -> Optional[date]:
        return phase.baseline_end if plan_basis == "baseline" else phase.current_end

    valid_ranges = [(start_of(p), end_of(p)) for p in phases if start_of(p) and end_of(p)]
    if not valid_ranges:
        return "No phases with valid dates found. Fill in milestone dates first."

    global_start = safe_min([s for s, _ in valid_ranges])
    global_end = safe_max([e for _, e in valid_ranges])
    assert global_start and global_end

    anchor = start_of_week_monday(global_start)
    total_weeks = compute_weeks_span(global_start, global_end)

    cell_width = 2  # each week cell is 2 characters wide: '■ '
    # Add one extra column so the closing ']' of a bar at the far right is always visible
    total_width = total_weeks * cell_width + 1

    # Left section widths for alignment
    phase_labels = [f"- Phase {p.number} – {p.name}" for p in phases]
    phase_w = max([len(s) for s in phase_labels] + [20])
    week_w = len("W 00-00")
    date_w = len("0000-00-00 to 0000-00-00")

    def left_prefix_text(phase: Phase, s: Optional[date], e: Optional[date], direction: str) -> str:
        left = f"{f'- Phase {phase.number} – {phase.name}':<{phase_w}} {format_week_label(s, e):<{week_w}} {format_date_range(s, e):<{date_w}} {direction} → "
        return left

    lines: List[str] = []

    for phase, phase_label in zip(phases, phase_labels):
        s = start_of(phase)
        e = end_of(phase)

        # Build background with spaces (no date marker for baseline)
        canvas = [" "] * total_width

        if s and e:
            # Compute block placement
            start_idx = compute_week_index(anchor, s)
            weeks_len = compute_weeks_span(s, e)
            block = "[" + ("■ " * weeks_len).rstrip() + "]"
            block_start_pos = start_idx * cell_width
            # Ensure canvas can fit block (clip if necessary)
            for j, ch in enumerate(block):
                pos = block_start_pos + j
                if 0 <= pos < total_width:
                    canvas[pos] = ch

        bar = "".join(canvas)

        # Direction: for baseline view, always show ▲ (no time-based comparison)
        direction = "▲"

        left_prefix = left_prefix_text(phase, s, e, direction)

        lines.append(f"{left_prefix}{bar}")

    return "\n".join(lines)


def replace_baseline_section(md: str, baseline_content: str, version: str) -> str:
    lines = md.splitlines()
    n = len(lines)
    # Locate the baseline heading for this version
    target_heading = f"## project baseline {version}".lower()
    heading_idx = None
    for idx, line in enumerate(lines):
        if line.strip().lower() == target_heading:
            heading_idx = idx
            break
    
    if heading_idx is None:
        # If not found, append at end
        new_block = [
            f"## Project Baseline {version}",
            "",
            "```text",
            *baseline_content.splitlines(),
            "```",
        ]
        return (md.rstrip() + "\n\n" + "\n".join(new_block) + "\n")
    
    # Find the end of existing baseline section: prefer closing code fence, otherwise next heading or EOF
    i = heading_idx + 1
    # Skip blank lines
    while i < n and lines[i].strip() == "":
        i += 1
    # If next is an opening fence, skip until matching closing fence
    if i < n and lines[i].strip().startswith("```"):
        i += 1
        while i < n and not lines[i].strip().startswith("```"):
            i += 1
        if i < n and lines[i].strip().startswith("```"):
            i += 1  # include closing fence
    else:
        # No fence; skip until next heading or EOF
        while i < n and not lines[i].strip().startswith("## "):
            i += 1
    
    # Build new content
    before = lines[:heading_idx]
    new_block = [
        lines[heading_idx],
        "",
        "```text",
        *baseline_content.splitlines(),
        "```",
    ]
    after = lines[i:]
    return "\n".join(before + new_block + after).rstrip() + "\n"


def replace_timeline_section(md: str, vb_block_content: str) -> str:
    lines = md.splitlines()
    n = len(lines)
    # Locate the timeline heading
    heading_idx = None
    for idx, line in enumerate(lines):
        if line.strip().lower().startswith("## project timeline"):
            heading_idx = idx
            break
    if heading_idx is None:
        # If not found, append at end
        new_block = [
            "## Project Timeline (Phases)",
            "",
            "```text",
            *vb_block_content.splitlines(),
            "```",
        ]
        return (md.rstrip() + "\n\n" + "\n".join(new_block) + "\n")

    # Find the end of existing timeline section: prefer closing code fence, otherwise next heading or EOF
    i = heading_idx + 1
    # Skip blank lines
    while i < n and lines[i].strip() == "":
        i += 1
    # If next is an opening fence, skip until matching closing fence
    if i < n and lines[i].strip().startswith("```"):
        i += 1
        while i < n and not lines[i].strip().startswith("```"):
            i += 1
        if i < n and lines[i].strip().startswith("```"):
            i += 1  # include closing fence
    else:
        # No fence; skip until next heading or EOF
        while i < n and not lines[i].strip().startswith("## "):
            i += 1

    # Build new content
    before = lines[:heading_idx]
    new_block = [
        lines[heading_idx],
        "",
        "```text",
        *vb_block_content.splitlines(),
        "```",
    ]
    after = lines[i:]
    return "\n".join(before + new_block + after).rstrip() + "\n"


# -----------------------------
# Template resource handling
# -----------------------------


def get_template_path(template_name: str) -> Path:
    """Get the path to a template file, trying package resources first, then local files."""
    try:
        # Try to use importlib.resources for packaged templates
        if hasattr(__import__('importlib.resources', fromlist=['files']), 'files'):
            from importlib.resources import files
            template_dir = files('pixel_planner') / 'templates'
            template_path = template_dir / template_name
            if template_path.is_file():
                return Path(str(template_path))
    except (ImportError, AttributeError, FileNotFoundError):
        pass
    
    # Fallback to local templates directory (for development/clone usage)
    local_template = Path("templates") / template_name
    if local_template.exists():
        return local_template
        
    # Last resort: try relative to this module
    module_dir = Path(__file__).parent.parent
    fallback_template = module_dir / "templates" / template_name
    if fallback_template.exists():
        return fallback_template
        
    raise FileNotFoundError(f"Template '{template_name}' not found in package or local directories")


# -----------------------------
# Commands
# -----------------------------


def cmd_init(template: Path, out_file: Path, project_name: Optional[str]) -> None:
    # If template is just a filename, try to resolve it from package resources
    if template.name == str(template) and not template.exists():
        try:
            template = get_template_path(str(template))
        except FileNotFoundError:
            pass  # Continue with original path for clearer error message
            
    content = read_text(template)
    if project_name:
        content = re.sub(
            r"^#\s+.*$",
            f"# {project_name} - High Level Plan",
            content,
            count=1,
            flags=re.MULTILINE,
        )
    write_text(out_file, content)
    print(f"Initialized plan at: {out_file}")


def cmd_timeline(
    in_file: Path,
    in_place: bool,
    out_file: Optional[Path],
    plan_basis: str,
    as_of: Optional[date],
    include_status: bool = False,
    baseline_version: str = "v1.0",
) -> None:
    md = read_text(in_file)
    phases = parse_markdown_for_phases(md)
    
    if plan_basis == "baseline":
        # Generate baseline timeline (no date markers)
        baseline_block = generate_baseline_block(phases, plan_basis=plan_basis)
        new_md = replace_baseline_section(md, baseline_block, baseline_version)
        section_name = f"baseline {baseline_version}"
    else:
        # Generate current timeline (with date markers)
        today = as_of or date.today()
        timeline_block = generate_timeline_block(phases, today, plan_basis=plan_basis)
        new_md = replace_timeline_section(md, timeline_block)
        section_name = "timeline"
    
    if include_status:
        status_graph = generate_status_graph(phases)
        new_md = replace_status_section(new_md, status_graph)
    
    if in_place:
        write_text(in_file, new_md)
        print(f"Updated {section_name} in: {in_file}")
        if include_status:
            print(f"Updated status overview in: {in_file}")
    else:
        assert out_file is not None
        write_text(out_file, new_md)
        print(f"Wrote {section_name} to: {out_file}")
        if include_status:
            print(f"Wrote status overview to: {out_file}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Pixel Planner automation")
    sub = p.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create a new project plan from a template")
    p_init.add_argument(
        "--template", 
        type=Path, 
        default="pixel-planner-phase-template.md", 
        help="Path to template file or template name (default: pixel-planner-phase-template.md)"
    )
    p_init.add_argument("--out", type=Path, required=True, help="Output Markdown plan file path")
    p_init.add_argument("--project", type=str, required=False, help="Project name to set in the plan header")

    p_tl = sub.add_parser("timeline", help="Generate or update the Project Timeline (Phases)")
    p_tl.add_argument("--in", dest="in_file", type=Path, required=True, help="Input Markdown plan file")
    p_tl.add_argument("--out", dest="out_file", type=Path, required=False, help="Output Markdown (if not in-place)")
    p_tl.add_argument("--in-place", dest="in_place", action="store_true", help="Rewrite the input file in place")
    p_tl.add_argument(
        "--basis",
        dest="basis",
        choices=["current", "baseline"],
        default="current",
        help="Use current plan dates or baseline dates for the timeline layout",
    )
    p_tl.add_argument(
        "--date",
        dest="as_of",
        type=str,
        required=False,
        help="Override 'today' (YYYY-MM-DD) for timeline generation",
    )
    p_tl.add_argument(
        "--include-status",
        dest="include_status",
        action="store_true",
        help="Include milestone status overview graph in addition to timeline",
    )
    p_tl.add_argument(
        "--version",
        dest="baseline_version",
        type=str,
        default="v1.0",
        help="Baseline version (only valid with --basis baseline, default: v1.0)",
    )

    return p


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command
    if command == "init":
        cmd_init(args.template, args.out, args.project)
    elif command == "timeline":
        if not args.in_place and not args.out_file:
            raise SystemExit("When not using --in-place, you must provide --out")
        
        # Validate version argument
        if args.baseline_version != "v1.0" and args.basis != "baseline":
            raise SystemExit("--version can only be used with --basis baseline")
            
        as_of_date: Optional[date] = None
        if args.as_of:
            try:
                as_of_date = datetime.strptime(args.as_of, DATE_FMT).date()
            except ValueError:
                raise SystemExit("--date must be in YYYY-MM-DD format")
        cmd_timeline(args.in_file, args.in_place, args.out_file, args.basis, as_of_date, args.include_status, args.baseline_version)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()