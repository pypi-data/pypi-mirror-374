import asyncio
import os
from skimly.client_enhanced import AsyncSkimlyClient, SkimlyClient, collect_stream

async def basic_chat_example():
    """Basic chat example with Anthropic Claude"""
    client = AsyncSkimlyClient(
        api_key=os.getenv("SKIMLY_KEY", "sk-test"),
        base_url=os.getenv("SKIMLY_BASE", "http://localhost:8000")
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
        
        print("Response:", response["content"][0]["text"])
        print("Tokens saved:", response["skimly_meta"]["tokens_saved"])
        print("Compression ratio:", response["skimly_meta"]["compression_ratio"])

async def streaming_chat_example():
    """Streaming chat example with OpenAI"""
    client = AsyncSkimlyClient.from_env()
    
    async with client:
        stream = client.messages.stream({
            "provider": "openai",
            "model": "gpt-4",
            "max_tokens": 1024,
            "messages": [{
                "role": "user", 
                "content": "Write a short story about a robot."
            }],
            "stream": True
        })
        
        print("Streaming response:")
        async for chunk in stream:
            if (chunk.get("type") == "content_block_delta" and 
                chunk.get("delta", {}).get("text")):
                print(chunk["delta"]["text"], end="", flush=True)
        print()

async def tool_calling_example():
    """Tool calling example"""
    client = AsyncSkimlyClient.from_env()
    
    async with client:
        response = await client.messages.create({
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022", 
            "max_tokens": 1024,
            "messages": [{
                "role": "user",
                "content": "What's the weather like in San Francisco?"
            }],
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

async def blob_management_example():
    """Blob management example"""
    client = AsyncSkimlyClient.from_env()
    
    # Large document
    large_doc = """
    This is a very large document that would consume many tokens.
    It contains extensive context about a project, codebase, or dataset.
    """ + "\n".join(f"Line {i}: More content here..." for i in range(1000))
    
    async with client:
        # Create blob
        blob_response = await client.create_blob(large_doc, "text/plain")
        blob_id = blob_response["blob_id"]
        print(f"Created blob: {blob_id}")
        
        # Use blob in chat with pointer
        response = await client.messages.create({
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Summarize this document:"
                    },
                    {
                        "type": "pointer", 
                        "blob_id": blob_id
                    }
                ]
            }]
        })
        
        print("Summary:", response["content"][0]["text"])
        print("Tokens saved:", response["skimly_meta"]["tokens_saved"])
        
        # Fetch blob content
        blob_content = await client.fetch_blob(blob_id)
        print("Fetched content length:", len(blob_content["content"]))
        
        # Transform tool result
        tool_result = '{"files": ["file1.py", "file2.py"], "analysis": "Complex analysis..."}'
        compressed = await client.transform(
            result=tool_result,
            tool_name="code_analysis",
            command="analyze_codebase", 
            model="claude-3-5-sonnet-20241022"
        )
        print("Compressed tool result:", compressed)

def sync_example():
    """Synchronous client example"""
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
    
    print("Sync response:", response["content"][0]["text"])

async def main():
    print("=== Basic Chat Example ===")
    await basic_chat_example()
    
    print("\\n=== Streaming Chat Example ===") 
    await streaming_chat_example()
    
    print("\\n=== Tool Calling Example ===")
    await tool_calling_example()
    
    print("\\n=== Blob Management Example ===")
    await blob_management_example()
    
    print("\\n=== Sync Client Example ===")
    sync_example()

if __name__ == "__main__":
    asyncio.run(main())