from __future__ import annotations
import os, json, time, requests
from typing import Any, Dict, List, Literal, Optional, Union
from .errors import SkimlyError, SkimlyHTTPError, SkimlyNetworkError
from .utils import cache_get_blob_id, cache_set_blob_id, sha256_hex

Provider = Literal['openai','anthropic']
Role = Literal['system','user','assistant']

class SkimlyClient:
    def __init__(self, key: str, base: Optional[str] = None, timeout_ms: int = 30000, retries: int = 2):
        if not key:
            raise SkimlyError("SKIMLY key required", 401)
        self.base = (base or "http://localhost:8000").rstrip("/")
        self.key = key
        self.timeout = timeout_ms / 1000  # Convert to seconds for requests
        self.retries = retries
        self._sess = requests.Session()

    @classmethod
    def from_env(cls) -> "SkimlyClient":
        base = os.getenv("SKIMLY_BASE", "http://localhost:8000")
        key = os.getenv("SKIMLY_KEY")
        if not key:
            raise SkimlyError("SKIMLY_KEY missing", 401)
        return cls(key=key, base=base)

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base}{path}"
        last_exc = None
        for attempt in range(self.retries + 1):
            try:
                r = self._sess.post(
                    url,
                    headers={"X-API-Key": self.key, "Content-Type": "application/json"},
                    data=json.dumps(payload),
                    timeout=self.timeout
                )
                if r.status_code >= 400:
                    # Retry 5xx errors only
                    if r.status_code >= 500 and attempt < self.retries:
                        time.sleep(0.2 * (2 ** attempt))
                        continue
                    raise SkimlyHTTPError(r.status_code, r.reason, r.text)
                return r.json()
            except (requests.Timeout, requests.ConnectionError) as e:
                last_exc = e
                if attempt < self.retries:
                    time.sleep(0.2 * (2 ** attempt))
                    continue
                raise SkimlyNetworkError("Network/timeout error", e)
        
        if last_exc:
            raise SkimlyNetworkError("Exhausted retries", last_exc)
        raise SkimlyError("Unknown request error")

    def _get(self, path: str) -> Dict[str, Any]:
        """Make a GET request with authentication"""
        url = f"{self.base}{path}"
        last_exc = None
        for attempt in range(self.retries + 1):
            try:
                r = self._sess.get(
                    url,
                    headers={"Authorization": f"Bearer {self.key}"},
                    timeout=self.timeout
                )
                if r.status_code >= 400:
                    # Retry 5xx errors only
                    if r.status_code >= 500 and attempt < self.retries:
                        time.sleep(0.2 * (2 ** attempt))
                        continue
                    raise SkimlyHTTPError(r.status_code, r.reason, r.text)
                return r.json()
            except (requests.Timeout, requests.ConnectionError) as e:
                last_exc = e
                if attempt < self.retries:
                    time.sleep(0.2 * (2 ** attempt))
                    continue
                raise SkimlyNetworkError("Network/timeout error", e)
        
        if last_exc:
            raise SkimlyNetworkError("Exhausted retries", last_exc)
        raise SkimlyError("Unknown request error")

    def _delete(self, path: str) -> Dict[str, Any]:
        """Make a DELETE request with authentication"""
        url = f"{self.base}{path}"
        last_exc = None
        for attempt in range(self.retries + 1):
            try:
                r = self._sess.delete(
                    url,
                    headers={"Authorization": f"Bearer {self.key}"},
                    timeout=self.timeout
                )
                if r.status_code >= 400:
                    # Retry 5xx errors only
                    if r.status_code >= 500 and attempt < self.retries:
                        time.sleep(0.2 * (2 ** attempt))
                        continue
                    raise SkimlyHTTPError(r.status_code, r.reason, r.text)
                return r.json()
            except (requests.Timeout, requests.ConnectionError) as e:
                last_exc = e
                if attempt < self.retries:
                    time.sleep(0.2 * (2 ** attempt))
                    continue
                raise SkimlyNetworkError("Network/timeout error", e)
        
        if last_exc:
            raise SkimlyNetworkError("Exhausted retries", last_exc)
        raise SkimlyError("Unknown request error")

    def create_blob(self, content: str, mime_type: str = "text/plain") -> Dict[str, str]:
        """Upload large context once; returns { blob_id }"""
        j = self._post("/v1/blobs", {"content": content, "mime_type": mime_type})
        if "blob_id" not in j:
            raise SkimlyError("missing blob_id in response")
        return {"blob_id": j["blob_id"]}

    def create_blob_if_new(self, content: str, mime_type: str = "text/plain") -> Dict[str, str]:
        """In-process dedupe: avoid re-uploading identical content this process has already sent"""
        h = sha256_hex(content)
        cached = cache_get_blob_id(h)
        if cached:
            return {"blob_id": cached}
        res = self.create_blob(content, mime_type)
        cache_set_blob_id(h, res["blob_id"])
        return res

    def chat(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """Chat with provider; messages may be string or array of parts ({type:'text'|'pointer', ...})"""
        # Default to uncompressed format for universal compatibility
        if 'response_format' not in req:
            req = {'response_format': 'uncompressed', **req}
        return self._post("/v1/chat", req)

    def messages(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """Create messages using the /v1/messages endpoint with uncompressed format by default"""
        # Default to uncompressed format for universal compatibility  
        if 'response_format' not in req:
            req = {'response_format': 'uncompressed', **req}
        return self._post("/v1/messages", req)

    def transform(self, result: str, tool_name: Optional[str] = None, command: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        """Transform and compress tool results using Smart Compression Timing"""
        payload = {"result": result}
        if tool_name:
            payload["tool_name"] = tool_name
        if command:
            payload["command"] = command
        if model:
            payload["model"] = model
        return self._post("/v1/transform", payload)

    def fetch(self, blob_id: str, start: Optional[int] = None, end: Optional[int] = None) -> Dict[str, Any]:
        """Fetch blob content with optional range support"""
        params = f"?ref={blob_id}"
        if start is not None:
            params += f"&start={start}"
        if end is not None:
            params += f"&end={end}"
        return self._get(f"/v1/fetch{params}")

    def get_signed_url(self, blob_id: str, ttl: int = 3600) -> Dict[str, Any]:
        """Get signed URL for direct blob access"""
        return self._get(f"/v1/blob/{blob_id}/signed?ttl={ttl}")

    def list_keys(self) -> Dict[str, Any]:
        """List API keys for the authenticated user"""
        return self._get("/v1/keys")

    def create_key(self, name: str) -> Dict[str, Any]:
        """Create a new API key"""
        return self._post("/v1/keys", {"name": name})

    def revoke_key(self, key_id: str) -> Dict[str, Any]:
        """Revoke an API key"""
        return self._delete(f"/v1/keys/{key_id}")

    def rotate_key(self, key_id: str) -> Dict[str, Any]:
        """Rotate an API key"""
        return self._post(f"/v1/keys/{key_id}", {"op": "rotate"})

# Alias for backward compatibility
Skimly = SkimlyClient
