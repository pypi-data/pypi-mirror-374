import asyncio
import json
from typing import List, Dict, Any
from skimly.client_enhanced import AsyncSkimlyClient, StreamingMessage, collect_stream

async def advanced_streaming_example():
    """Advanced streaming with message collection and processing"""
    client = AsyncSkimlyClient.from_env()
    
    async with client:
        # Start streaming
        stream = client.messages.stream({
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "temperature": 0.7,
            "messages": [{
                "role": "user",
                "content": "Write a technical analysis of Python asyncio with code examples"
            }],
            "stream": True
        })
        
        # Method 1: Manual streaming with progress tracking
        streaming_msg = StreamingMessage()
        chunk_count = 0
        
        print("Streaming response (with progress):")
        print("-" * 50)
        
        async for chunk in stream:
            streaming_msg.add_chunk(chunk)
            chunk_count += 1
            
            # Print progress
            if chunk.get("type") == "content_block_delta":
                delta_text = chunk.get("delta", {}).get("text", "")
                print(delta_text, end="", flush=True)
                
            elif chunk.get("type") == "message_start":
                print(f"[Message started: {chunk.get('message', {}).get('id', 'unknown')}]")
                
            elif chunk.get("type") == "message_stop":
                print(f"\\n[Message completed after {chunk_count} chunks]")
                break
        
        # Get final message
        final_message = streaming_msg.message
        print(f"\\nFinal message length: {len(streaming_msg.get_text())} characters")
        print(f"Tokens saved: {final_message['skimly_meta']['tokens_saved']}")

async def streaming_with_tools_example():
    """Streaming with tool calling"""
    client = AsyncSkimlyClient.from_env()
    
    async with client:
        stream = client.messages.stream({
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{
                "role": "user",
                "content": "What's the current time and weather in New York?"
            }],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_current_time",
                        "description": "Get the current time",
                        "parameters": {"type": "object", "properties": {}}
                    }
                },
                {
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
                }
            ],
            "stream": True
        })
        
        print("Streaming with tools:")
        print("-" * 50)
        
        streaming_msg = StreamingMessage()
        
        async for chunk in stream:
            streaming_msg.add_chunk(chunk)
            
            if chunk.get("type") == "content_block_delta":
                if "text" in chunk.get("delta", {}):
                    print(chunk["delta"]["text"], end="", flush=True)
                    
            elif chunk.get("type") == "content_block_start":
                content_block = chunk.get("content_block", {})
                if content_block.get("type") == "tool_use":
                    print(f"\\n[Tool use: {content_block.get('name')}]")
                    
            elif chunk.get("type") == "message_stop":
                break
        
        # Check for tool uses
        tool_uses = streaming_msg.get_tool_uses()
        if tool_uses:
            print(f"\\n\\nTool uses detected: {len(tool_uses)}")
            for tool_use in tool_uses:
                print(f"- {tool_use.get('name')}: {tool_use.get('input')}")

async def collect_stream_example():
    """Using collect_stream helper"""
    client = AsyncSkimlyClient.from_env()
    
    async with client:
        print("Using collect_stream helper:")
        print("-" * 50)
        
        stream = client.messages.stream({
            "provider": "openai",
            "model": "gpt-4",
            "max_tokens": 512,
            "messages": [{
                "role": "user",
                "content": "Explain quantum computing in simple terms"
            }],
            "stream": True
        })
        
        # Collect entire stream into final message
        message = await collect_stream(stream)
        
        print("Complete message received:")
        print(message["content"][0]["text"])
        print(f"\\nUsage: {message['usage']}")
        print(f"Compression: {message['skimly_meta']['compression_ratio']:.2f}x")

async def error_handling_example():
    """Error handling in streaming"""
    client = AsyncSkimlyClient(
        api_key="invalid-key",
        base_url="http://localhost:8000"
    )
    
    try:
        async with client:
            stream = client.messages.stream({
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-20241022", 
                "max_tokens": 100,
                "messages": [{
                    "role": "user",
                    "content": "Hello"
                }],
                "stream": True
            })
            
            async for chunk in stream:
                print("Chunk:", chunk)
                
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}: {e}")

async def parallel_streaming_example():
    """Multiple concurrent streams"""
    client = AsyncSkimlyClient.from_env()
    
    async def create_stream(prompt: str, model: str) -> str:
        async with client:
            stream = client.messages.stream({
                "provider": "openai" if model.startswith("gpt") else "anthropic",
                "model": model,
                "max_tokens": 256,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "stream": True
            })
            
            message = await collect_stream(stream)
            return message["content"][0]["text"]
    
    print("Parallel streaming:")
    print("-" * 50)
    
    # Run multiple streams concurrently
    tasks = [
        create_stream("What is Python?", "gpt-4"),
        create_stream("What is JavaScript?", "claude-3-5-sonnet-20241022"),
        create_stream("What is Rust?", "gpt-4")
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Stream {i+1} failed: {result}")
        else:
            print(f"Stream {i+1}: {result[:100]}...")

async def main():
    print("=== Advanced Streaming Example ===")
    await advanced_streaming_example()
    
    print("\\n\\n=== Streaming with Tools ===")
    await streaming_with_tools_example()
    
    print("\\n\\n=== Collect Stream Example ===")  
    await collect_stream_example()
    
    print("\\n\\n=== Error Handling Example ===")
    await error_handling_example()
    
    print("\\n\\n=== Parallel Streaming Example ===")
    await parallel_streaming_example()

if __name__ == "__main__":
    asyncio.run(main())