# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Thinkers Dinning** is an agentic philosophical statement refinement system using the Agno framework. Two specialized AI agents collaborate iteratively:

- **Aphoristicor Agent** (OpenAI gpt-4o): Creates and refines philosophical statements
- **Assessor Agent** (Anthropic Claude-3.5-Sonnet): Critically evaluates statements and provides structured assessments

The workflow continues until a statement achieves a 10/10 ranking or reaches maximum iterations (100).

## Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install agno python-dotenv

# Configure environment
cp .env.example .env
# Edit .env with API keys: OPENAI_API_KEY and ANTHROPIC_API_KEY
```

### Running the System
```bash
# Run with custom statement
python main.py "Your philosophical statement here"

# Run interactively (prompts for input)
python main.py

# Run with default test statement
python main.py

# Test setup without running full workflow
python test_setup.py
```

## Architecture

### Core Components
- **`main.py`**: CLI interface and environment validation
- **`workflow.py`**: Main orchestration logic with iteration loop
- **`agents.py`**: Agent implementations with structured outputs
- **`models.py`**: Pydantic data models for type safety
- **`logger.py`**: Markdown session logging system

### Data Flow
1. User provides initial philosophical statement
2. **Assessment Phase**: Assessor evaluates statement → returns `AssessorResponse` with embedded `Assessment`
3. **Refinement Phase**: If ranking < target, Aphoristicor refines → returns `AphoristicorResponse`
4. Repeat until target ranking achieved or max iterations reached

### Key Data Models
```python
# Core assessment structure
Assessment(overview, strengths[], weaknesses[], ranking: 1-10, reasoning)

# Agent responses
AssessorResponse(assessment: Assessment, ready_for_next: bool)
AphoristicorResponse(refined_statement: str, explanation: str, iteration: int)

# Session tracking
WorkflowSession(session_id, statements, interactions[], completion_status)
```

## Agno Framework Integration

### Critical Patterns
- Set `response_model` on Agent constructor (not `run()` method)
- Use `gpt-4o` for OpenAI structured outputs (not `gpt-4-turbo`)
- Access structured data via `response.content` from agent methods
- Import: `from agno.models.openai import OpenAIChat` and `from agno.models.anthropic import Claude`

### Agent Structure
```python
class MyAgent:
    def __init__(self):
        self.agent = Agent(
            name="AgentName",
            model=OpenAIChat(id="gpt-4o"),  # Or Claude(id="claude-3-5-sonnet-20241022")
            response_model=ResponseModel,   # Set here, not in run()
            introduction="System prompt..."
        )
    
    def process(self, input_data) -> ResponseModel:
        response = self.agent.run("Prompt here")
        return response.content  # Returns Pydantic model instance
```

### Environment Requirements
- `OPENAI_API_KEY`: Required for Aphoristicor agent
- `ANTHROPIC_API_KEY`: Required for Assessor agent
- Optional: `AGNO_API_KEY` for Agno-specific features

## Session Logging

All workflow sessions automatically generate timestamped markdown logs with:
- Session metadata and configuration
- Iteration-by-iteration assessment and refinement details  
- Final results and completion status

Files named: `{statement_keywords}_{timestamp}.md`

## Testing

Use `python test_setup.py` to validate:
- Environment configuration and API keys
- Module imports (agno, pydantic, local modules)
- Pydantic model creation and structure