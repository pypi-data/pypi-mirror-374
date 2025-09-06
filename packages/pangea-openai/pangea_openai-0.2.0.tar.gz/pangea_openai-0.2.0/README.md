# Pangea + OpenAI Python API library

A wrapper around the OpenAI Python library that wraps the [Responses API](https://platform.openai.com/docs/api-reference/responses)
with Pangea AI Guard. Supports Python v3.10 and greater.

## Installation

```bash
pip install -U pangea-openai
```

## Usage

```python
import os
from pangea_openai import PangeaOpenAI

client = PangeaOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    # Pangea options
    pangea_api_key=os.environ.get("PANGEA_API_KEY"),
    pangea_input_recipe="pangea_prompt_guard",
    pangea_output_recipe="pangea_llm_response_guard",
)

response = client.responses.create(
    model="gpt-4o",
    instructions="You are a coding assistant that talks like a pirate.",
    input="How do I check if a Python object is an instance of a class?",
)

print(response.output_text)
```

## Microsoft Azure OpenAI

To use this library with [Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/overview),
use the `PangeaAzureOpenAI` class instead of the `PangeaOpenAI` class.

```python
from pangea_openai import PangeaAzureOpenAI

client = PangeaAzureOpenAI(
    # https://learn.microsoft.com/azure/ai-services/openai/reference#rest-api-versioning
    api_version="2023-07-01-preview",
    # https://learn.microsoft.com/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
    azure_endpoint="https://example-endpoint.openai.azure.com",
    # Pangea options
    pangea_api_key=os.environ.get("PANGEA_API_KEY"),
    pangea_input_recipe="pangea_prompt_guard",
    pangea_output_recipe="pangea_llm_response_guard",
)

completion = client.chat.completions.create(
    model="deployment-name",  # e.g. gpt-35-instant
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.to_json())
```
