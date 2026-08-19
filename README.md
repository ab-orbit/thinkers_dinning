# Thinkers Dinning - Agentic Philosophical Statement Refinement

An agentic system where two AI agents collaborate to iteratively refine philosophical statements through critical assessment and improvement.

## Overview

This project implements an agentic workflow with two specialized agents that collaborate to refine philosophical statements through iterative assessment and improvement. The workflow continues until the statement achieves a ranking of 10/10 or reaches the maximum number of iterations (100).

## System Architecture

### Agents
1. **Aphoristicor Agent** (OpenAI gpt-4o)
   - Creates and refines philosophical statements
   - Reviews assessment feedback and rewrites statements
   - Maintains core meaning while addressing identified weaknesses
   - Preserves assessed strengths
   - Uses structured outputs for consistent response format

2. **Assessor Agent** (Anthropic Claude-3.5-Sonnet)  
   - Critically evaluates philosophical statements from epistemological and scientific reasoning perspectives
   - Returns structured assessment with:
     - Overview: Comprehensive assessment summary
     - Strengths: What works well philosophically and logically
     - Weaknesses: Critical flaws in reasoning, clarity, or validity
     - Ranking: 1-10 score based on logical coherence, epistemological validity, clarity, scientific compatibility, and philosophical depth
     - Reasoning: Detailed justification for the ranking

### Workflow Process
1. User provides initial philosophical statement
2. **Assessment Phase**: Assessor evaluates the statement and provides structured feedback
3. **Refinement Phase**: If ranking < target (default 10), Aphoristicor refines statement based on assessment
4. Process repeats until either:
   - Statement achieves target ranking (success), OR
   - Maximum iterations reached (100 by default)

## Setup and Installation

### Prerequisites
- Python 3.8+
- OpenAI API key
- Anthropic API key

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd thinkers_dinning

# Install dependencies
pip install agno python-dotenv

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# OPENAI_API_KEY=your_openai_api_key
# ANTHROPIC_API_KEY=your_anthropic_api_key
```

### Usage
```bash
# Run with command line argument
python main.py "Your philosophical statement here"

# Run interactively
python main.py

# Run with default test statement
python main.py
```

## Technical Implementation

### Framework and Libraries
- **Framework**: [Agno](https://docs.agno.com/) for agent orchestration and structured outputs
- **Data Models**: Pydantic for type-safe structured data
- **Environment**: python-dotenv for configuration management

### Models Used
- **Aphoristicor**: OpenAI gpt-4o (supports structured outputs)
- **Assessor**: Anthropic claude-3-5-sonnet-20241022

### File Structure
```
├── main.py              # Entry point and CLI interface
├── workflow.py          # Main workflow orchestration
├── agents.py            # Agent implementations (Aphoristicor & Assessor)
├── models.py            # Pydantic data models
├── logger.py            # Markdown logging system
├── .env.example         # Environment variables template
└── README.md           # This file
```

### Data Models
- `PhilosophicalStatement`: Statement with iteration tracking
- `Assessment`: Structured evaluation results
- `AphoristicorResponse`: Refined statement with explanation
- `AssessorResponse`: Assessment wrapper
- `WorkflowSession`: Complete session state and history
- `InteractionLog`: Individual interaction records

### Logging
All sessions are automatically logged to timestamped markdown files with:
- Session metadata and configuration
- Iteration-by-iteration assessment and refinement details
- Final results and completion status

## Research Pipeline Monitor

Alongside the philosophical refinement workflow, this repo also ships a
standalone CLI for installing and monitoring the 8-stage research pipeline
promised by the [ai-research-skills](https://github.com/WenyuChiou/ai-research-skills)
catalog (literature -> gap -> design -> build -> run -> visualise -> write ->
submit).

### Install the agents (Claude Code plugins)
```bash
bash scripts/install_research_agents.sh          # core + all optional plugins, project scope
bash scripts/install_research_agents.sh --core-only
```

### Monitor pipeline progress
```bash
# List the 16 agents/skills and (if the `claude` CLI is on PATH) their install status
python pipeline_monitor.py agents

# Check which pipeline stages a research project has completed, based on
# the artifacts each skill is contracted to emit (design_brief.md,
# project_manifest.yml, claims.yml, ...)
python pipeline_monitor.py status --path /path/to/research/project

# Keep watching, refreshing every 30 seconds
python pipeline_monitor.py status --path /path/to/research/project --watch 30

# Machine-readable output
python pipeline_monitor.py status --path /path/to/research/project --json
```

Stages 4 (Build the model) and 6 (Visualise & interpret) have no
machine-checkable manifest in the catalog, so they're tracked manually via
an optional `.research/pipeline_state.yml` file in the monitored project:
```yaml
stage_4: done
stage_6: done
```

## Example Usage

### Default Test Statement
"Reality is as complex as the human [in]capacity to comprehend it"

### Sample Output
```
🧠 Thinkers Dinning - Philosophical Statement Refinement
============================================================
✅ Environment configuration validated

📝 Processing statement: 'Reality is as complex as the human [in]capacity to comprehend it'

🚀 Starting Philosophical Refinement Workflow
Session ID: a1b2c3d4
Initial Statement: 'Reality is as complex as the human [in]capacity to comprehend it'
Target Ranking: 10/10
Max Iterations: 100
Log File: reality_complex_human_20240109_120000.md
--------------------------------------------------------------------------------

🔄 Iteration 1
🧠 Assessor evaluating statement...
📊 Assessment Result:
   Ranking: 5/10
   Strengths: 4 identified
   Weaknesses: 6 identified
✏️  Aphoristicor refining statement...
📝 Statement refined
   Original: 'Reality is as complex as the human [in]capacity to compr...'
   Refined:  'The complexity we perceive in reality corresponds to...'
```