# llm-usage-tracker

A drop-in token and cost tracker for popular LLM libraries with caching awareness. Automatically tracks usage across multiple LLM providers by monkey-patching their API calls.

## Features

- **Zero-config tracking**: Just import and start tracking
- **Multi-provider support**: OpenAI, LiteLLM, Google Gemini
- **Cost calculation**: Automatic cost computation based on current pricing
- **Session management**: Track usage across different sessions
- **Caching awareness**: Handles cached responses appropriately

## Supported Libraries

- OpenAI v1 (client + module-level)
- OpenAI v0 (legacy `ChatCompletion.create`)
- LiteLLM (optional)
- Google `google-generativeai` (optional)

## Installation

```bash
pip install -e .

# With optional dependencies:
pip install -e .[litellm]  # For LiteLLM support
pip install -e .[gemini]   # For Google Gemini support
pip install -e .[all]      # All optional dependencies
```

## Quick Start

```python
from llm_usage_tracker import setup_patch, print_usage_costs

# Enable tracking
setup_patch()

# Your existing OpenAI/LiteLLM/Gemini code works unchanged
import openai
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Print usage summary
print_usage_costs()
```

## Usage with Sessions

```python
from llm_usage_tracker import UsageSession

with UsageSession("my-session") as session:
    # Your LLM calls here
    pass

# Get session costs
costs = session.compute_costs()
print(f"Total cost: ${costs['total_cost']:.4f}")
```

## License

MIT
