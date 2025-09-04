from __future__ import annotations
import os
import json
import time
import asyncio
from typing import Any, Dict, List, Optional, Union, AsyncIterator, cast
import httpx
from .types_enhanced import (
    MessageParams, MessageResponse, StreamingChunk, 
    BlobCreateResponse, BlobFetchResponse, RequestOptions,
    SkimlyClientOptions, SkimlyError, SkimlyAPIError, SkimlyNetworkError,
    SkimlyAuthenticationError, SkimlyPermissionError, SkimlyNotFoundError,
    SkimlyRateLimitError, SkimlyInternalServerError
)
from .utils import cache_get_blob_id, cache_set_blob_id, sha256_hex

class AsyncSkimlyClient:
    def __init__(
        self, 
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: int = 30000,
        max_retries: int = 2,
        default_headers: Optional[Dict[str, str]] = None
    ):
        if not api_key:
            raise SkimlyError("SKIMLY API key required", 401)
        
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout / 1000  # Convert to seconds
        self.max_retries = max_retries
        self.default_headers = default_headers or {}
        
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
                **self.default_headers
            }
        )

    @classmethod
    def from_env(cls) -> "AsyncSkimlyClient":
        base_url = os.getenv("SKIMLY_BASE", "http://localhost:8000")
        api_key = os.getenv("SKIMLY_KEY")
        if not api_key:
            raise SkimlyError("SKIMLY_KEY missing", 401)
        return cls(api_key=api_key, base_url=base_url)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()

    async def _request(
        self, 
        method: str, 
        path: str, 
        data: Optional[Dict[str, Any]] = None,
        options: Optional[RequestOptions] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = {**self.default_headers}
        if options and options.get("headers"):
            headers.update(options["headers"])
        
        timeout = (options.get("timeout", self.timeout * 1000) / 1000 
                  if options else self.timeout)
        max_retries = options.get("max_retries", self.max_retries) if options else self.max_retries

        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                response = await self._client.request(
                    method,
                    url,
                    json=data,
                    headers=headers,
                    timeout=httpx.Timeout(timeout)
                )
                
                if response.status_code >= 400:
                    await self._handle_error_response(response, attempt, max_retries)
                
                return response.json()
                
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_exception = e
                if attempt < max_retries:
                    await asyncio.sleep(0.2 * (2 ** attempt))
                    continue
                raise SkimlyNetworkError(f"Network/timeout error: {e}", cause=e)
        
        if last_exception:
            raise SkimlyNetworkError("Exhausted retries", cause=last_exception)
        raise SkimlyError("Unknown request error")

    async def _handle_error_response(self, response: httpx.Response, attempt: int, max_retries: int):
        status = response.status_code
        headers = dict(response.headers)
        
        try:
            body = response.json()
        except:
            body = response.text

        # Retry 5xx errors only
        if status >= 500 and attempt < max_retries:
            await asyncio.sleep(0.2 * (2 ** attempt))
            return
        
        # Map to specific error types
        if status == 401:
            raise SkimlyAuthenticationError("Authentication failed", headers=headers, body=body)
        elif status == 403:
            raise SkimlyPermissionError("Permission denied", headers=headers, body=body)
        elif status == 404:
            raise SkimlyNotFoundError("Resource not found", headers=headers, body=body)
        elif status == 429:
            raise SkimlyRateLimitError("Rate limit exceeded", headers=headers, body=body)
        elif status >= 500:
            raise SkimlyInternalServerError("Internal server error", headers=headers, body=body)
        else:
            raise SkimlyAPIError(f"HTTP {status}", status, headers=headers, body=body)

    @property
    def messages(self):
        return MessagesResource(self)

    async def create_message(
        self, 
        params: MessageParams, 
        options: Optional[RequestOptions] = None
    ) -> MessageResponse:
        if params.get("stream"):
            raise SkimlyError("Use stream_messages() for streaming requests", 400)
        
        return cast(MessageResponse, await self._request("POST", "/v1/chat", params, options))

    async def stream_messages(
        self,
        params: MessageParams,
        options: Optional[RequestOptions] = None
    ) -> AsyncIterator[StreamingChunk]:
        # Ensure streaming is enabled
        stream_params = {**params, "stream": True}
        
        url = f"{self.base_url}/v1/chat"
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            **self.default_headers
        }
        if options and options.get("headers"):
            headers.update(options["headers"])
        
        timeout = (options.get("timeout", self.timeout * 1000) / 1000 
                  if options else self.timeout)

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    url,
                    json=stream_params,
                    headers=headers,
                    timeout=httpx.Timeout(timeout)
                ) as response:
                    if response.status_code >= 400:
                        text = await response.aread()
                        raise SkimlyAPIError(
                            f"HTTP {response.status_code}",
                            response.status_code,
                            headers=dict(response.headers),
                            body=text.decode()
                        )

                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line or not line.startswith("data: "):
                            continue
                        
                        data = line[6:]  # Remove "data: " prefix
                        if data == "[DONE]":
                            return
                        
                        try:
                            chunk: StreamingChunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
                            
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise SkimlyNetworkError(f"Streaming error: {e}", cause=e)

    async def create_blob(
        self,
        content: str,
        mime_type: str = "text/plain",
        options: Optional[RequestOptions] = None
    ) -> BlobCreateResponse:
        response = await self._request(
            "POST", 
            "/v1/blobs", 
            {"content": content, "mime_type": mime_type},
            options
        )
        return cast(BlobCreateResponse, response)

    async def create_blob_if_new(
        self,
        content: str,
        mime_type: str = "text/plain", 
        options: Optional[RequestOptions] = None
    ) -> BlobCreateResponse:
        hash_key = sha256_hex(content)
        cached = cache_get_blob_id(hash_key)
        if cached:
            return {"blob_id": cached}
        
        result = await self.create_blob(content, mime_type, options)
        cache_set_blob_id(hash_key, result["blob_id"])
        return result

    async def fetch_blob(
        self,
        blob_id: str,
        range_params: Optional[Dict[str, int]] = None,
        options: Optional[RequestOptions] = None
    ) -> BlobFetchResponse:
        path = f"/v1/fetch?ref={blob_id}"
        if range_params:
            if "start" in range_params:
                path += f"&start={range_params['start']}"
            if "end" in range_params:
                path += f"&end={range_params['end']}"
        
        response = await self._request("GET", path, options=options)
        return cast(BlobFetchResponse, response)

    async def transform(
        self,
        result: str,
        tool_name: Optional[str] = None,
        command: Optional[str] = None,
        model: Optional[str] = None,
        options: Optional[RequestOptions] = None
    ) -> Dict[str, Any]:
        payload = {"result": result}
        if tool_name:
            payload["tool_name"] = tool_name
        if command:
            payload["command"] = command
        if model:
            payload["model"] = model
        
        return await self._request("POST", "/v1/transform", payload, options)

    async def get_signed_url(
        self,
        blob_id: str,
        ttl: int = 3600,
        options: Optional[RequestOptions] = None
    ) -> Dict[str, Any]:
        return await self._request("GET", f"/v1/blob/{blob_id}/signed?ttl={ttl}", options=options)

    async def list_keys(self, options: Optional[RequestOptions] = None) -> Dict[str, Any]:
        return await self._request("GET", "/v1/keys", options=options)

    async def create_key(self, name: str, options: Optional[RequestOptions] = None) -> Dict[str, Any]:
        return await self._request("POST", "/v1/keys", {"name": name}, options)

    async def revoke_key(self, key_id: str, options: Optional[RequestOptions] = None) -> Dict[str, Any]:
        return await self._request("DELETE", f"/v1/keys/{key_id}", options=options)

    async def rotate_key(self, key_id: str, options: Optional[RequestOptions] = None) -> Dict[str, Any]:
        return await self._request("POST", f"/v1/keys/{key_id}", {"op": "rotate"}, options)


class MessagesResource:
    def __init__(self, client: AsyncSkimlyClient):
        self._client = client

    async def create(
        self, 
        params: MessageParams, 
        options: Optional[RequestOptions] = None
    ) -> MessageResponse:
        return await self._client.create_message(params, options)

    def stream(
        self,
        params: MessageParams,
        options: Optional[RequestOptions] = None
    ) -> AsyncIterator[StreamingChunk]:
        return self._client.stream_messages(params, options)


class StreamingMessage:
    def __init__(self):
        self.chunks: List[StreamingChunk] = []
        self._message: Dict[str, Any] = {
            "id": "",
            "type": "message",
            "role": "assistant", 
            "content": [],
            "model": "",
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 0, "output_tokens": 0},
            "skimly_meta": {
                "provider": "openai",
                "model": "",
                "tokens_saved": 0,
                "compression_ratio": 0,
                "original_tokens": 0,
                "compressed_tokens": 0,
                "processing_time_ms": 0
            }
        }

    @property
    def message(self) -> Dict[str, Any]:
        return dict(self._message)

    def add_chunk(self, chunk: StreamingChunk) -> None:
        self.chunks.append(chunk)
        self._process_chunk(chunk)

    def _process_chunk(self, chunk: StreamingChunk) -> None:
        chunk_type = chunk.get("type")
        
        if chunk_type == "message_start":
            if "message" in chunk:
                self._message.update(chunk["message"])
                
        elif chunk_type == "content_block_start":
            if "content_block" in chunk and "index" in chunk:
                if not isinstance(self._message["content"], list):
                    self._message["content"] = []
                index = chunk["index"]
                # Extend list if needed
                while len(self._message["content"]) <= index:
                    self._message["content"].append({"type": "text", "text": ""})
                self._message["content"][index] = chunk["content_block"]
                
        elif chunk_type == "content_block_delta":
            if "delta" in chunk and "index" in chunk:
                index = chunk["index"]
                delta = chunk["delta"]
                if (isinstance(self._message["content"], list) and 
                    index < len(self._message["content"])):
                    content = self._message["content"][index]
                    if content.get("type") == "text" and "text" in delta:
                        content["text"] = content.get("text", "") + delta["text"]
                        
        elif chunk_type == "message_delta":
            if "delta" in chunk:
                self._message.update(chunk["delta"])

    def is_complete(self) -> bool:
        return any(chunk.get("type") == "message_stop" for chunk in self.chunks)

    def get_text(self) -> str:
        content = self._message.get("content", [])
        if isinstance(content, list):
            return "".join(
                block.get("text", "") 
                for block in content 
                if block.get("type") == "text"
            )
        return ""

    def get_tool_uses(self) -> List[Dict[str, Any]]:
        content = self._message.get("content", [])
        if isinstance(content, list):
            return [
                block for block in content 
                if block.get("type") == "tool_use"
            ]
        return []


async def collect_stream(
    stream: AsyncIterator[StreamingChunk]
) -> MessageResponse:
    streaming_message = StreamingMessage()
    
    async for chunk in stream:
        streaming_message.add_chunk(chunk)
    
    if not streaming_message.is_complete():
        raise SkimlyError("Stream ended before message was complete")
    
    return cast(MessageResponse, streaming_message.message)


# Sync wrapper for backwards compatibility
class SkimlyClient:
    def __init__(self, *args, **kwargs):
        self._async_client = AsyncSkimlyClient(*args, **kwargs)
        self._loop = None

    def _get_loop(self):
        if self._loop is None:
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop

    def _run_async(self, coro):
        loop = self._get_loop()
        if loop.is_running():
            # If loop is already running, we need to use run_in_executor
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)

    @classmethod
    def from_env(cls):
        return cls(**AsyncSkimlyClient.from_env().__dict__)

    def create_message(self, params, options=None):
        return self._run_async(self._async_client.create_message(params, options))

    def create_blob(self, content, mime_type="text/plain", options=None):
        return self._run_async(self._async_client.create_blob(content, mime_type, options))

    def create_blob_if_new(self, content, mime_type="text/plain", options=None):
        return self._run_async(self._async_client.create_blob_if_new(content, mime_type, options))

    def fetch_blob(self, blob_id, range_params=None, options=None):
        return self._run_async(self._async_client.fetch_blob(blob_id, range_params, options))

    def transform(self, result, tool_name=None, command=None, model=None, options=None):
        return self._run_async(self._async_client.transform(result, tool_name, command, model, options))

    # Legacy method names for compatibility
    def chat(self, req):
        return self.create_message(req)

    def create_blob(self, content, mime_type="text/plain"):
        return self._run_async(self._async_client.create_blob(content, mime_type))

    def fetch(self, blob_id, start=None, end=None):
        range_params = {}
        if start is not None:
            range_params["start"] = start
        if end is not None:
            range_params["end"] = end
        return self._run_async(self._async_client.fetch_blob(blob_id, range_params if range_params else None))


# Keep old alias
Skimly = SkimlyClient