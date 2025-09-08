```python
from agno.agent import Agent, RunResponse
from agno.models.anthropic import Claude

agent = Agent(
    model=Claude(id="claude-3-5-sonnet-20240620"),
    markdown=True
)

# Print the response on the terminal
agent.print_response("Share a 2 sentence horror story.")
```

```python
from os import getenv
from agno.agent import Agent, RunResponse
from agno.models.openai.like import OpenAILike

agent = Agent(
    model=OpenAILike(
        id="mistralai/Mixtral-8x7B-Instruct-v0.1",
        api_key=getenv("TOGETHER_API_KEY"),
        base_url="https://api.together.xyz/v1",
    )
)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story.")
```

```python
from agno.agent import Agent, RunResponse
from agno.models.deepseek import DeepSeek

agent = Agent(model=DeepSeek(), markdown=True)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story.")
```

```python
from agno.agent import Agent, RunResponse
from agno.models.groq import Groq

agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    markdown=True
)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story.")
```