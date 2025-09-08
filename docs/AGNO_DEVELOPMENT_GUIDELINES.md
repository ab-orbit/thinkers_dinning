# Agno Agent Development Guidelines

This document captures critical lessons learned from developing the Thinkers Dinning project and provides guidelines for future agno agent development.

## Core Agno Framework Patterns

### 1. Structured Outputs Setup

**✅ Correct Pattern:**
```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from pydantic import BaseModel

class MyResponse(BaseModel):
    field1: str
    field2: int

# Set response_model when creating the agent
agent = Agent(
    name="MyAgent",
    model=OpenAIChat(id="gpt-4o"),  # Use models that support structured outputs
    response_model=MyResponse,
    introduction="System prompt here..."
)

# Simple run call
response = agent.run("User message here")
# response.content is now a MyResponse instance
return response.content
```

**❌ Common Mistakes:**
- Using `structured_output` parameter instead of `response_model`
- Passing `response_model` to `run()` instead of `Agent()` constructor
- Using models that don't support structured outputs (like `gpt-4-turbo`)

### 2. Model Selection for Structured Outputs

**OpenAI Models:**
- ✅ `gpt-4o` - Recommended, supports structured outputs
- ✅ `gpt-4o-mini` - Supports structured outputs, faster/cheaper
- ❌ `gpt-4-turbo` - Does NOT support structured outputs with json_schema

**Anthropic Models:**
- ✅ `claude-3-5-sonnet-20241022` - Supports structured outputs
- ✅ `claude-3-5-haiku-20241022` - Supports structured outputs

### 3. Response Structure Understanding

When using `response_model`, the agno Agent returns:
```python
RunResponse.content -> YourPydanticModel
```

**Access Pattern:**
```python
# In agent method
response = self.agent.run(prompt)
return response.content  # This is your Pydantic model instance

# In workflow
agent_response = agent.some_method()
# agent_response is now YourPydanticModel, access fields directly
data = agent_response.field_name
```

## Import Patterns

### Correct Imports
```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
```

### ❌ Incorrect Imports to Avoid
```python
# These don't exist or are incorrect
from agno.models.openai import OpenAI
from agno.models.openai import OpenAIModel
from agno.models.openai.like import OpenAILike  # Only for non-OpenAI compatible APIs
```

## Agent Design Patterns

### 1. Agent Class Structure
```python
class MyAgent:
    def __init__(self):
        self.agent = Agent(
            name="descriptive_name",
            model=ModelClass(id="model_id"),
            response_model=ResponseModel,
            introduction="""Clear system prompt that defines:
            - Agent role and expertise
            - Expected input/output format
            - Task-specific instructions
            - Quality criteria"""
        )
    
    def specific_task(self, input_data: InputType) -> ResponseModel:
        prompt = f"""Specific instructions for this task:
        Input: {input_data}
        
        Task details...
        Format requirements...
        """
        
        response = self.agent.run(prompt)
        return response.content
```

### 2. Error Handling
```python
try:
    agent_response = self.agent_instance.method(input_data)
    # Process successful response
    result = agent_response.expected_field
except Exception as e:
    print(f"❌ Error in agent method: {str(e)}")
    # Handle gracefully - log, retry, or use fallback
```

## Data Model Design

### Pydantic Model Best Practices
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Assessment(BaseModel):
    overview: str = Field(description="Clear description of field purpose")
    strengths: List[str] = Field(description="List of identified strengths")
    weaknesses: List[str] = Field(description="List of critical issues")
    ranking: int = Field(ge=1, le=10, description="Numerical score with constraints")
    reasoning: str = Field(description="Detailed justification")
    timestamp: datetime = Field(default_factory=datetime.now)

class ResponseWrapper(BaseModel):
    assessment: Assessment = Field(description="Nested model for complex data")
    ready_for_next: bool = Field(description="Control flow indicator")
```

## Environment Configuration

### Required Setup
```python
from dotenv import load_dotenv
import os

def setup_environment():
    load_dotenv()
    
    required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        print("❌ Missing required environment variables:")
        for key in missing_keys:
            print(f"   - {key}")
        sys.exit(1)
```

### .env.example Template
```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Configuration  
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Agno Configuration
AGNO_DEBUG=true
AGNO_LOG_LEVEL=INFO
```

## Workflow Orchestration

### Agent Interaction Pattern
```python
class MyWorkflow:
    def __init__(self):
        self.agent1 = Agent1()
        self.agent2 = Agent2()
    
    def run(self, input_data):
        for iteration in range(max_iterations):
            # Step 1: First agent processes
            try:
                response1 = self.agent1.process(input_data)
                data = response1.expected_field
            except Exception as e:
                print(f"❌ Error in agent1: {str(e)}")
                continue
            
            # Step 2: Second agent processes
            try:
                response2 = self.agent2.process(data)
                # Check completion conditions
                if response2.completion_criteria:
                    return success_result
            except Exception as e:
                print(f"❌ Error in agent2: {str(e)}")
                continue
```

## Common Troubleshooting

### Issues and Solutions

1. **"'RunResponse' object has no attribute 'field_name'"**
   - Solution: Access via `response.content.field_name`

2. **"Invalid parameter: 'response_format' not supported"**
   - Solution: Use `gpt-4o` instead of `gpt-4-turbo` for structured outputs

3. **"cannot import name 'OpenAI' from 'agno.models.openai'"**
   - Solution: Use `OpenAIChat` instead of `OpenAI`

4. **Structured output not working**
   - Check: Set `response_model` on Agent constructor, not `run()` method
   - Check: Model supports structured outputs (gpt-4o, not gpt-4-turbo)

### Debug Patterns
```python
# Enable debug mode
workflow = Workflow(debug_mode=True)

# Log response structure for investigation
print(f"Response type: {type(response)}")
print(f"Response content type: {type(response.content)}")
print(f"Response structure: {response}")
```

## Performance Considerations

- Use `gpt-4o-mini` for faster, cheaper operations when full `gpt-4o` capability isn't needed
- Implement retry logic with exponential backoff for API calls
- Cache expensive computations when possible
- Use streaming responses for long-running operations
- Monitor token usage and implement cost controls

## Testing Strategies

```python
# Test agent responses
def test_agent_response():
    agent = MyAgent()
    test_input = "test case"
    
    response = agent.process(test_input)
    
    # Validate structure
    assert isinstance(response, ExpectedResponseModel)
    assert response.required_field is not None
    
    # Validate content quality
    assert len(response.list_field) > 0
    assert 1 <= response.ranking <= 10
```

This guide should be referenced for all future agno-based agent development to avoid the common pitfalls encountered in this project.