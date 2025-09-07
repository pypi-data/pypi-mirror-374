# PrabhatAI

A thin Python wrapper for the OpenRouter chat completions API.

## Installation
```bash
pip install prabhatai
```

## Usage

### 1. Install locally
Navigate to the `PrabhatAI` directory and run:

```bash
pip install .
```

### 2. Use in your Python code
By default, the package uses the included API key and the free DeepSeek model, with a safe default for max_tokens.

```python
from prabhatai.client import PrabhatAIClient
client = PrabhatAIClient()  # Uses default API key and model
response = client.chat([
    {"role": "user", "content": "Hello!"}
])
print(response)
```

#### To use your own API key
Set the environment variable:

```bash
export OPENROUTER_API_KEY="sk-or-...your-key..."
```
Or pass it directly:

```python
client = PrabhatAIClient(api_key="sk-or-...your-key...")
```

#### To use a different model or max_tokens

```python
response = client.chat([
    {"role": "user", "content": "Hello!"}
], model="openai/gpt-4o", max_tokens=500)
```

The default max_tokens is set to 1000 to avoid quota errors for free accounts.
