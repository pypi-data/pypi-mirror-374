from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

Json = Dict[str, Any]

@dataclass
class RequestOptions:
    timeout: Optional[float] = 30.0
    headers: Optional[Dict[str, str]] = None

@dataclass
class InferRequest:
    prompt: str
    profile: Optional[str] = None
    stream: Optional[bool] = None

@dataclass
class InferResponse:
    output_text: Optional[str]
    provider: Optional[str] = None
    model_id: Optional[str] = None
    task: Optional[str] = None
    profile: Optional[str] = None
    latency_ms: Optional[int] = None
    usage: Optional[Json] = None
    raw: Optional[Any] = None

@dataclass
class InvokeRequest:
    messages: Optional[Iterable[Json]] = None
    input: Optional[Json] = None
    parameters: Optional[Json] = None
    stream: Optional[bool] = None

@dataclass
class StreamEvent:
    data: str


__all__ = [
    "Json",
    "RequestOptions",
    "InferRequest",
    "InferResponse",
    "InvokeRequest",
    "StreamEvent",
]
