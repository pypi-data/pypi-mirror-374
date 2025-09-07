from .client import SkimlyClient, Skimly
from .client_enhanced import AsyncSkimlyClient, StreamingMessage, collect_stream
from .verify import verify_skimly_signature
from .types import (
    Provider, Mode, Role, TextPart, PointerPart, MessagePart, Message,
    ChatRequest, SkimlyMeta, ChatResponse, BlobCreateRequest, BlobCreateResponse
)
from .types_enhanced import (
    MessageParams, MessageResponse, StreamingChunk, BlobCreateResponse as EnhancedBlobCreateResponse,
    BlobFetchResponse, ContentBlock, Tool, ToolUse, ToolResult, Usage,
    SkimlyClientOptions, RequestOptions
)
from .errors import SkimlyError, SkimlyHTTPError, SkimlyNetworkError
from .utils import sha256_hex, cache_get_blob_id, cache_set_blob_id

__all__ = [
    # Legacy client
    "SkimlyClient", "Skimly", 
    # Enhanced async client
    "AsyncSkimlyClient", "StreamingMessage", "collect_stream",
    # Verification
    "verify_skimly_signature",
    # Legacy types
    "Provider", "Mode", "Role", "TextPart", "PointerPart", "MessagePart", "Message",
    "ChatRequest", "SkimlyMeta", "ChatResponse", "BlobCreateRequest", "BlobCreateResponse",
    # Enhanced types
    "MessageParams", "MessageResponse", "StreamingChunk", "EnhancedBlobCreateResponse",
    "BlobFetchResponse", "ContentBlock", "Tool", "ToolUse", "ToolResult", "Usage",
    "SkimlyClientOptions", "RequestOptions",
    # Errors
    "SkimlyError", "SkimlyHTTPError", "SkimlyNetworkError",
    # Utils
    "sha256_hex", "cache_get_blob_id", "cache_set_blob_id"
]
