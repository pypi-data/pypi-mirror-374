# Skimly Python SDK

A production-grade Python SDK for Skimly - the drop-in gateway for AI-powered coding tools that reduces output token usage through smart compression.

## Features

- 🚀 **Full Type Hints** - Complete type annotations with dataclasses and TypedDict
- 🌊 **Async Streaming** - Real-time streaming with AsyncIterator support
- 🛠️ **Tool Calling** - Complete tool calling interface with helper functions
- 📦 **Blob Management** - Large content handling with automatic deduplication
- ⚡ **Performance** - Built-in retry logic, timeouts, and connection pooling
- 🔄 **Provider Agnostic** - Works with OpenAI, Anthropic, and other providers
- 💾 **Smart Caching** - Automatic blob deduplication to reduce costs
- 🔀 **Sync & Async** - Both synchronous and asynchronous clients

## Installation

```bash
pip install skimly
```

## Quick Start

```python
from skimly import AsyncSkimlyClient

async def main():
    client = AsyncSkimlyClient(
        api_key="sk-your-api-key",
        base_url="https://api.skimly.com"
    )
    
    async with client:
        response = await client.messages.create({
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{
                "role": "user",
                "content": "Hello, world!"
            }]
        })
        
        print(response["content"][0]["text"])
        print("Tokens saved:", response["skimly_meta"]["tokens_saved"])

import asyncio
asyncio.run(main())
```

## Streaming

```python
async def streaming_example():
    client = AsyncSkimlyClient.from_env()
    
    async with client:
        stream = client.messages.stream({
            "provider": "openai",
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Write a story"}],
            "stream": True
        })
        
        async for chunk in stream:
            if chunk.get("type") == "content_block_delta":
                if text := chunk.get("delta", {}).get("text"):
                    print(text, end="", flush=True)
```

## Tool Calling

```python
async def tool_calling_example():
    client = AsyncSkimlyClient.from_env()
    
    async with client:
        response = await client.messages.create({
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "messages": [{"role": "user", "content": "What's the weather in SF?"}],
            "tools": [{
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"}
                        },
                        "required": ["location"]
                    }
                }
            }]
        })
        
        # Check for tool uses
        tool_uses = [
            block for block in response["content"]
            if block.get("type") == "tool_use"
        ]
        print("Tool uses:", tool_uses)
```

## Blob Management

```python
async def blob_example():
    client = AsyncSkimlyClient.from_env()
    
    # Large document
    large_doc = "Very large document content..." * 1000
    
    async with client:
        # Upload blob
        blob_response = await client.create_blob(large_doc)
        blob_id = blob_response["blob_id"]
        
        # Use in chat with pointer
        response = await client.messages.create({
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Summarize this:"},
                    {"type": "pointer", "blob_id": blob_id}
                ]
            }]
        })
        
        print("Summary:", response["content"][0]["text"])
        print("Tokens saved:", response["skimly_meta"]["tokens_saved"])
        
        # Automatic deduplication
        deduped = await client.create_blob_if_new(large_doc)
        print("Same blob ID:", deduped["blob_id"] == blob_id)
```

## Environment Setup

```bash
export SKIMLY_KEY=sk-your-api-key
export SKIMLY_BASE=https://api.skimly.com
```

```python
from skimly import AsyncSkimlyClient
client = AsyncSkimlyClient.from_env()
```

## Error Handling

```python
from skimly import (
    SkimlyError,
    SkimlyAPIError,
    SkimlyAuthenticationError,
    SkimlyRateLimitError
)

try:
    response = await client.messages.create(params)
except SkimlyAuthenticationError:
    print("Invalid API key")
except SkimlyRateLimitError:
    print("Rate limit exceeded")
except SkimlyAPIError as e:
    print(f"API error {e.status}: {e.message}")
```

## Configuration

```python
client = AsyncSkimlyClient(
    api_key="sk-your-key",
    base_url="https://api.skimly.com",
    timeout=60000,        # 60 seconds
    max_retries=3,        # Retry failed requests
    default_headers={
        "User-Agent": "MyApp/1.0"
    }
)
```

## Synchronous Client

For non-async environments:

```python
from skimly import SkimlyClient

client = SkimlyClient.from_env()

response = client.create_message({
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 1024,
    "messages": [{
        "role": "user",
        "content": "Hello from sync client!"
    }]
})

print(response["content"][0]["text"])
```

## Advanced Usage

### Streaming Collection

```python
from skimly import collect_stream

stream = client.messages.stream(params)
message = await collect_stream(stream)
print(message["content"][0]["text"])
```

### Streaming Message Helper

```python
from skimly import StreamingMessage

streaming_msg = StreamingMessage()

async for chunk in stream:
    streaming_msg.add_chunk(chunk)
    
    if streaming_msg.is_complete():
        break

print("Final text:", streaming_msg.get_text())
print("Tool uses:", streaming_msg.get_tool_uses())
```

### Transform Tool Results

```python
compressed = await client.transform(
    result=json.dumps(tool_output),
    tool_name="code_analysis",
    command="analyze_files",
    model="claude-3-5-sonnet-20241022"
)
```

### Fetch with Range

```python
content = await client.fetch_blob(
    blob_id, 
    range_params={"start": 0, "end": 1000}
)
```

## Type Hints

Complete type definitions are included:

```python
from skimly.types_enhanced import (
    MessageParams,
    MessageResponse,
    StreamingChunk,
    ContentBlock,
    Tool,
    SkimlyClientOptions
)
```

## Examples

See the [examples](./examples/) directory for complete usage examples:

- [Basic Usage](./examples/basic_usage.py) - Simple chat, streaming, and tools
- [Advanced Streaming](./examples/advanced_streaming.py) - Complex streaming scenarios

## Requirements

- Python 3.8+
- httpx
- typing_extensions (Python < 3.11)

## License

MIT
