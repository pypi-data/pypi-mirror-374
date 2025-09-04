from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Union, AsyncIterator, TypedDict
from dataclasses import dataclass
from enum import Enum

Provider = Literal['openai', 'anthropic']
Role = Literal['system', 'user', 'assistant']

class TextContent(TypedDict):
    type: Literal['text']
    text: str

class PointerContent(TypedDict):
    type: Literal['pointer']
    blob_id: str

class ImageContent(TypedDict):
    type: Literal['image']
    source: Dict[str, Any]

ContentBlock = Union[TextContent, PointerContent, ImageContent]

class Message(TypedDict):
    role: Role
    content: Union[str, List[ContentBlock]]

class ToolFunction(TypedDict, total=False):
    name: str
    description: Optional[str]
    parameters: Optional[Dict[str, Any]]
    input_schema: Optional[Dict[str, Any]]

class Tool(TypedDict):
    type: Literal['function']
    function: ToolFunction

class ToolChoice(TypedDict, total=False):
    type: Literal['function']
    function: Dict[str, str]

class ToolUse(TypedDict):
    type: Literal['tool_use']
    id: str
    name: str
    input: Dict[str, Any]

class ToolResult(TypedDict, total=False):
    type: Literal['tool_result']
    tool_use_id: str
    content: Optional[Union[str, List[ContentBlock]]]
    is_error: Optional[bool]

class BaseMessageParams(TypedDict, total=False):
    model: str
    messages: List[Message]
    max_tokens: Optional[int]
    temperature: Optional[float]
    top_p: Optional[float]
    top_k: Optional[int]
    stop: Optional[Union[str, List[str]]]
    system: Optional[str]
    tools: Optional[List[Tool]]
    tool_choice: Optional[Union[str, ToolChoice]]
    stream: Optional[bool]

class AnthropicMessageParams(BaseMessageParams):
    provider: Literal['anthropic']

class OpenAIMessageParams(BaseMessageParams):
    provider: Literal['openai']
    frequency_penalty: Optional[float]
    presence_penalty: Optional[float]
    logit_bias: Optional[Dict[str, float]]
    user: Optional[str]
    seed: Optional[int]

MessageParams = Union[AnthropicMessageParams, OpenAIMessageParams]

class Usage(TypedDict):
    input_tokens: int
    output_tokens: int
    total_tokens: Optional[int]

class SkimlyMeta(TypedDict):
    provider: Provider
    model: str
    tokens_saved: int
    compression_ratio: float
    original_tokens: int
    compressed_tokens: int
    processing_time_ms: int

class MessageResponse(TypedDict):
    id: str
    type: Literal['message']
    role: Literal['assistant']
    content: List[ContentBlock]
    model: str
    stop_reason: Literal['end_turn', 'max_tokens', 'stop_sequence', 'tool_use']
    stop_sequence: Optional[str]
    usage: Usage
    skimly_meta: SkimlyMeta

class StreamingChunk(TypedDict, total=False):
    type: Literal['message_start', 'message_delta', 'content_block_start', 'content_block_delta', 'content_block_stop', 'message_stop']
    index: Optional[int]
    delta: Optional[Dict[str, Any]]
    message: Optional[Dict[str, Any]]
    content_block: Optional[ContentBlock]

class BlobCreateResponse(TypedDict):
    blob_id: str

class BlobFetchResponse(TypedDict, total=False):
    content: str
    metadata: Optional[Dict[str, Any]]

class RequestOptions(TypedDict, total=False):
    timeout: Optional[int]
    max_retries: Optional[int]
    headers: Optional[Dict[str, str]]

class SkimlyClientOptions(TypedDict, total=False):
    api_key: str
    base_url: Optional[str]
    timeout: Optional[int]
    max_retries: Optional[int]
    default_headers: Optional[Dict[str, str]]

@dataclass
class SkimlyError(Exception):
    message: str
    status: int = 500
    
    def __str__(self) -> str:
        return f"SkimlyError({self.status}): {self.message}"

@dataclass
class SkimlyAPIError(SkimlyError):
    headers: Optional[Dict[str, str]] = None
    body: Optional[Any] = None

@dataclass 
class SkimlyAuthenticationError(SkimlyAPIError):
    def __post_init__(self):
        self.status = 401

@dataclass
class SkimlyPermissionError(SkimlyAPIError):
    def __post_init__(self):
        self.status = 403

@dataclass
class SkimlyNotFoundError(SkimlyAPIError):
    def __post_init__(self):
        self.status = 404

@dataclass
class SkimlyRateLimitError(SkimlyAPIError):
    def __post_init__(self):
        self.status = 429

@dataclass
class SkimlyInternalServerError(SkimlyAPIError):
    def __post_init__(self):
        self.status = 500

@dataclass
class SkimlyNetworkError(SkimlyError):
    cause: Optional[Exception] = None
    
    def __post_init__(self):
        self.status = 503