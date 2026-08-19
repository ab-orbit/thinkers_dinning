#!/usr/bin/env python3
"""
Research Pipeline Monitor

A simple CLI that tracks progress through the 8-stage research pipeline
promised by the ai-research-skills catalog (github.com/WenyuChiou/ai-research-skills):

    1. Discover literature   -> 2. Find the gap        -> 3a. Frame the RQ
 -> 3b. Plan the project     -> 4. Build the model      -> 5. Run & validate
 -> 6. Visualise & interpret -> 7. Draft the manuscript -> 8. Submit + respond

Each stage's completion is detected by looking for the artifact(s) the
matching Claude Code skill(s) are contracted to emit (topic_dossier.gaps.yml,
design_brief.md, project_manifest.yml, claims.yml, ...). Stages 4 and 6 have
no machine-checkable manifest in the catalog, so they are tracked manually
via an optional `.research/pipeline_state.yml` override file.

Usage:
    python pipeline_monitor.py status [--path DIR] [--json] [--watch SECONDS]
    python pipeline_monitor.py agents [--json]
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".idea", "logs"}

STAGES = [
    {
        "id": "1",
        "title": "Discover literature",
        "skills": ["research-hub", "paper-summarize"],
        "patterns": ["*.bib"],
        "manual": False,
    },
    {
        "id": "2",
        "title": "Find the gap",
        "skills": [
            "gap-to-topic",
            "literature-triage-matrix",
            "notebooklm-brief-verifier",
            "zotero-library-curator",
        ],
        "patterns": ["*.gaps.yml", "topic_dossier.md"],
        "manual": False,
    },
    {
        "id": "3a",
        "title": "Frame the RQ",
        "skills": ["research-design-helper"],
        "patterns": ["design_brief.md"],
        "manual": False,
    },
    {
        "id": "3b",
        "title": "Plan the project",
        "skills": ["research-context-compressor", "research-project-orienter"],
        "patterns": ["project_manifest.yml"],
        "manual": False,
    },
    {
        "id": "4",
        "title": "Build the model",
        "skills": ["codex-delegate"],
        "patterns": [],
        "manual": True,
    },
    {
        "id": "5",
        "title": "Run & validate",
        "skills": ["research-context-compressor", "research-project-orienter"],
        "patterns": ["experiment_matrix.yml", "run_log.md"],
        "manual": False,
    },
    {
        "id": "6",
        "title": "Visualise & interpret",
        "skills": ["codex-delegate", "gemini-delegate"],
        "patterns": [],
        "manual": True,
    },
    {
        "id": "7",
        "title": "Draft the manuscript",
        "skills": ["paper-memory-builder", "academic-writing-skills"],
        "patterns": ["claims.yml", "figures.yml"],
        "manual": False,
    },
    {
        "id": "8",
        "title": "Submit + respond",
        "skills": ["academic-writing-skills", "research-context-compressor"],
        "patterns": ["reviewer-response.md"],
        "manual": False,
    },
]

# name -> (family, purpose, stage ids)
AGENTS = {
    "research-hub": ("research-workspace", "Search, ingest, organise papers across Zotero / Obsidian / NotebookLM.", ["1"]),
    "paper-summarize": ("research-workspace", "Fill per-paper Key Findings / Methodology / Relevance notes.", ["1"]),
    "gap-to-topic": ("research-workspace", "3-gate go/no-go decision dossier for a candidate thesis topic.", ["2"]),
    "literature-triage-matrix": ("research-workspace", "Comparison matrix across method, data, claim, limitation.", ["2"]),
    "notebooklm-brief-verifier": ("research-workspace", "Verify NotebookLM briefs against source bundles.", ["2"]),
    "zotero-library-curator": ("research-workspace", "Audit a Zotero library; preview-only cleanup plans.", ["2"]),
    "research-design-helper": ("research-workspace", "Socratic walk from RQ to mechanism, identifiability, validation, risk.", ["3a"]),
    "research-context-compressor": ("research-workspace", "Write .research/ manifests so future AI sessions skip the rescan.", ["3b", "5", "8"]),
    "research-project-orienter": ("research-workspace", "Fast orientation memo from .research/ manifests.", ["3b", "5"]),
    "research-hub-multi-ai": ("research-workspace", "Router across Claude / Codex / Gemini delegates.", []),
    "paper-memory-builder": ("research-workspace", "Extract .paper/claims.yml and .paper/figures.yml for manuscript work.", ["7"]),
    "academic-writing-skills": ("academic-writing", "Outlines, drafting, evidence alignment, release readiness.", ["7", "8"]),
    "paper-review": ("academic-writing", "Cross-disciplinary evidence-safe scientific review.", ["7", "8"]),
    "zotero-skills": ("zotero-operations", "Deep Zotero CRUD, collections, tags, item edits.", []),
    "codex-delegate": ("ai-delegation", "Leaf delegate for token-heavy mechanical coding work.", ["4", "6"]),
    "gemini-delegate": ("ai-delegation", "Leaf delegate for long-context, CJK, or second-opinion work.", ["6"]),
}

PLUGINS = [
    "research-workspace",
    "academic-writing-skills",
    "zotero-skills",
    "codex-delegate",
    "gemini-delegate",
]


def find_matches(root: Path, patterns: List[str]) -> List[Path]:
    matches = []
    for pattern in patterns:
        for path in root.rglob(pattern):
            if any(part in EXCLUDE_DIRS for part in path.parts):
                continue
            matches.append(path)
    return sorted(set(matches))


def load_manual_overrides(root: Path) -> dict:
    """Read `.research/pipeline_state.yml` for manually-confirmed stages.

    Kept dependency-free: parses simple `stage_<id>: done` lines rather than
    pulling in a YAML library for one flat key/value file.
    """
    state_file = root / ".research" / "pipeline_state.yml"
    overrides = {}
    if not state_file.exists():
        return overrides

    for raw_line in state_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip("'\"")
        if key.startswith("stage_"):
            overrides[key[len("stage_"):]] = value.lower() in {"done", "true", "yes", "complete"}
    return overrides


def evaluate_stage(root: Path, stage: dict, overrides: dict) -> dict:
    override = overrides.get(stage["id"])
    if stage["manual"]:
        done = bool(override)
        artifacts = []
    else:
        artifacts = find_matches(root, stage["patterns"])
        done = bool(artifacts) if override is None else override

    return {**stage, "done": done, "artifacts": artifacts}


def check_cross_cutting(root: Path) -> dict:
    plan = find_matches(root, [str(Path(".coord") / "multi_ai_plan.md")])
    return {"active": bool(plan), "artifacts": plan}


def claude_plugin_list() -> Optional[str]:
    try:
        result = subprocess.run(
            ["claude", "plugin", "list"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def build_status(root: Path) -> dict:
    overrides = load_manual_overrides(root)
    stages = [evaluate_stage(root, stage, overrides) for stage in STAGES]
    completed = sum(1 for s in stages if s["done"])

    current = None
    for stage in stages:
        if not stage["done"]:
            current = stage["id"]
            break

    return {
        "root": str(root.resolve()),
        "stages": stages,
        "cross_cutting": {"research-hub-multi-ai": check_cross_cutting(root)},
        "completed": completed,
        "total": len(stages),
        "current_stage": current,
    }


def render_status(status: dict) -> str:
    lines = []
    lines.append("Research Pipeline Monitor")
    lines.append(f"  target : {status['root']}")
    lines.append(
        f"  progress: {status['completed']}/{status['total']} checkpoints complete "
        "(8-stage pipeline; stage 3 split into 3a design + 3b plan)"
    )
    lines.append("")

    for stage in status["stages"]:
        mark = "✅" if stage["done"] else ("○" if stage["manual"] else "⏳")
        pointer = " <-- current" if stage["id"] == status["current_stage"] else ""
        lines.append(f"  [{mark}] Stage {stage['id']:<2} {stage['title']}{pointer}")
        lines.append(f"        skills: {', '.join(stage['skills']) or '-'}")
        if stage["manual"]:
            lines.append(
                "        manual stage - mark done with `stage_%s: done` in .research/pipeline_state.yml"
                % stage["id"]
            )
        elif stage["artifacts"]:
            for artifact in stage["artifacts"][:5]:
                lines.append(f"        found: {artifact}")
            if len(stage["artifacts"]) > 5:
                lines.append(f"        ... and {len(stage['artifacts']) - 5} more")
        else:
            lines.append(f"        waiting on: {', '.join(stage['patterns'])}")
        lines.append("")

    router = status["cross_cutting"]["research-hub-multi-ai"]
    router_mark = "✅" if router["active"] else "—"
    lines.append(f"  [{router_mark}] cross-cutting: research-hub-multi-ai (.coord/multi_ai_plan.md)")

    return "\n".join(lines)


def cmd_status(args: argparse.Namespace) -> None:
    root = Path(args.path).expanduser()
    if not root.exists():
        print(f"error: path does not exist: {root}", file=sys.stderr)
        sys.exit(1)

    def emit():
        status = build_status(root)
        if args.json:
            print(json.dumps(status, indent=2, default=str))
        else:
            print(render_status(status))
        return status

    if not args.watch:
        emit()
        return

    try:
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            status = emit()
            print(f"\n(refreshing every {args.watch}s, press Ctrl+C to stop)")
            if status["completed"] == status["total"]:
                print("\U0001f389 all 8 stages complete")
            time.sleep(args.watch)
    except KeyboardInterrupt:
        print("\nstopped watching.")


def cmd_agents(args: argparse.Namespace) -> None:
    live_output = claude_plugin_list()

    def is_installed(family: str) -> Optional[bool]:
        if live_output is None:
            return None
        return family in live_output and "✔" in live_output.split(family, 1)[1].split("\n", 1)[0]

    if args.json:
        payload = {
            "agents": [
                {
                    "name": name,
                    "family": family,
                    "purpose": purpose,
                    "stages": stages,
                }
                for name, (family, purpose, stages) in AGENTS.items()
            ],
            "claude_cli_available": live_output is not None,
        }
        print(json.dumps(payload, indent=2))
        return

    print("ai-research-skills agents (16 total)")
    if live_output is None:
        print("  (claude CLI not found on PATH - showing catalog only, no live install status)")
    print("")

    by_family = {}
    for name, (family, purpose, stages) in AGENTS.items():
        by_family.setdefault(family, []).append((name, purpose, stages))

    for family, items in by_family.items():
        plugin_name = family if family in PLUGINS else items[0][0]
        installed = is_installed(plugin_name)
        badge = "✅" if installed else ("❓" if installed is None else "❌")
        print(f"{badge} {family}")
        for name, purpose, stages in items:
            stage_label = ", ".join(stages) if stages else "cross-cutting"
            print(f"    - {name} (stage {stage_label}): {purpose}")
        print("")

    print("Install with: bash scripts/install_research_agents.sh")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pipeline_monitor.py",
        description="Monitor progress through the ai-research-skills 8-stage research pipeline.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Show pipeline stage progress for a research project directory.")
    status_parser.add_argument("--path", default=".", help="Research project directory to inspect (default: current directory)")
    status_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of text")
    status_parser.add_argument("--watch", type=int, default=0, metavar="SECONDS", help="Re-check and redraw every SECONDS until Ctrl+C")
    status_parser.set_defaults(func=cmd_status)

    agents_parser = subparsers.add_parser("agents", help="List the ai-research-skills agents/skills and their install status.")
    agents_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of text")
    agents_parser.set_defaults(func=cmd_agents)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
