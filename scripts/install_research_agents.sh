#!/usr/bin/env bash
# install_research_agents.sh — install the ai-research-skills agents
# (github.com/WenyuChiou/ai-research-skills) as Claude Code plugins for
# this project, so pipeline_monitor.py has real agents to track.
#
# Usage:
#   bash scripts/install_research_agents.sh              # core + all optional plugins
#   bash scripts/install_research_agents.sh --core-only   # just research-workspace (11 skills)
#   bash scripts/install_research_agents.sh --scope user  # install for all projects instead of this one
#
# Prerequisite: Claude Code CLI on PATH (`claude --version`).

set -euo pipefail

MARKETPLACE="WenyuChiou/ai-research-skills"
CORE_PLUGIN="research-workspace"
OPTIONAL_PLUGINS=(
  "academic-writing-skills"
  "zotero-skills"
  "codex-delegate"
  "gemini-delegate"
)

SCOPE="project"
CORE_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)
      SCOPE="${2:?--scope requires a value (project|user)}"
      shift 2
      ;;
    --core-only)
      CORE_ONLY=1
      shift
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if ! command -v claude >/dev/null 2>&1; then
  echo "error: 'claude' CLI not found on PATH." >&2
  echo "Install Claude Code first: https://claude.ai/code" >&2
  exit 1
fi

echo ">> Adding marketplace: $MARKETPLACE"
claude plugin marketplace add "$MARKETPLACE"

echo ""
echo ">> Installing $CORE_PLUGIN (scope: $SCOPE)"
claude plugin install "$CORE_PLUGIN@ai-research-skills" --scope "$SCOPE"

if [[ "$CORE_ONLY" -eq 0 ]]; then
  for p in "${OPTIONAL_PLUGINS[@]}"; do
    echo ""
    echo ">> Installing $p (scope: $SCOPE)"
    claude plugin install "$p@ai-research-skills" --scope "$SCOPE"
  done
fi

echo ""
echo "Done. Run 'claude plugin list' to confirm the plugins show as enabled,"
echo "then track pipeline progress with:"
echo "  python pipeline_monitor.py agents"
echo "  python pipeline_monitor.py status --watch 30"
