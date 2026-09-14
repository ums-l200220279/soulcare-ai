from __future__ import annotations

import hashlib
import json
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable

from fastapi import Request

JsonDict = dict[str, object]


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        with self._lock:
            queue = self._requests[key]
            while queue and queue[0] < window_start:
                queue.popleft()
            if len(queue) >= self.limit:
                return False
            queue.append(now)
            return True


class IdempotencyStore:
    def __init__(self, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self._entries: dict[str, tuple[float, str, JsonDict]] = {}
        self._lock = threading.Lock()

    def get(self, key: str, payload_hash: str) -> JsonDict | None:
        now = time.time()
        with self._lock:
            self._purge(now)
            value = self._entries.get(key)
            if value is None:
                return None
            _, stored_hash, response = value
            if stored_hash != payload_hash:
                raise ValueError("idempotency_key_payload_mismatch")
            return response

    def set(self, key: str, payload_hash: str, response: JsonDict) -> None:
        with self._lock:
            self._entries[key] = (time.time(), payload_hash, response)

    def _purge(self, now: float) -> None:
        expired = [k for k, (created_at, _, _) in self._entries.items() if now - created_at > self.ttl_seconds]
        for key in expired:
            del self._entries[key]


def request_id_from_headers(request: Request) -> str:
    request_id = request.headers.get("X-Request-ID")
    if request_id:
        return request_id[:128]
    return hashlib.sha256(f"{time.time()}:{id(request)}".encode("utf-8")).hexdigest()[:16]


def payload_hash(payload: JsonDict) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def safe_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()[:64]
    if request.client and request.client.host:
        return request.client.host[:64]
    return "unknown"


def trace_context(request: Request) -> Callable[[str], JsonDict]:
    request_id = request.state.request_id
    client_ip = request.state.client_ip

    def build(event: str) -> JsonDict:
        return {
            "event": event,
            "request_id": request_id,
            "client_ip": client_ip,
            "method": request.method,
            "path": request.url.path,
        }

    return build
