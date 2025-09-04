# Prompt Studio SDK

A Python SDK for fetching and rendering prompts from Prompt Studio API.

## Installation

```bash
pip install just-prompt-sdk
```

## Usage

### Standalone rendering
```python
from prompt_studio import render

rendered = render("Hello, {{name}}!", {"name": "World"})
print(rendered)  # Output: Hello, World!
```

### With API integration
```python
from prompt_studio import PromptStudio, render

studio = PromptStudio(api_key="your-api-key")
prompt = studio.get_prompt("my-project", "my-prompt")
rendered = render(prompt, {"name": "World"})
```

## License

MIT License