from __future__ import annotations
from typing import Any, Dict, Generator, Iterable, Optional

import httpx

from ..errors import APIError
from ..types import InferRequest, InferResponse, StreamEvent

class RouterResource:
    def __init__(self, client: Any) -> None:
        self._client = client

    def infer(self, request: InferRequest) -> InferResponse:
        url = f"{self._client.base_url}/v1/infer"
        payload = {k: v for k, v in request.__dict__.items() if v is not None}
        with self._client._client() as c:  # pylint: disable=protected-access
            req = c.build_request("POST", url, json=payload)
            resp = self._client._retry_send(c, req)  # pylint: disable=protected-access
            if resp.status_code >= 400:
                raise APIError(resp.status_code, resp.text, body=resp.text)
            data = resp.json()
            return InferResponse(**data)

    def stream(self, request: InferRequest) -> Generator[StreamEvent, None, None]:
        url = f"{self._client.base_url}/v1/infer"
        payload = {k: v for k, v in request.__dict__.items() if v is not None}
        payload["stream"] = True
        with self._client._client() as c:  # pylint: disable=protected-access
            req = c.build_request("POST", url, json=payload)
            resp = c.send(req, stream=True)
            if resp.status_code >= 400:
                raise APIError(resp.status_code, resp.text, body=resp.text)
            yield from self._client._iter_stream(resp)  # pylint: disable=protected-access

    # Async variants
    async def ainfer(self, request: InferRequest) -> InferResponse:
        url = f"{self._client.base_url}/v1/infer"
        payload = {k: v for k, v in request.__dict__.items() if v is not None}
        async with self._client._client() as c:  # pylint: disable=protected-access
            resp = await c.post(url, json=payload)
            if resp.status_code >= 400:
                raise APIError(resp.status_code, resp.text, body=await resp.aread())
            data = resp.json()
            return InferResponse(**data)

    async def astream(self, request: InferRequest):
        url = f"{self._client.base_url}/v1/infer"
        payload = {k: v for k, v in request.__dict__.items() if v is not None}
        payload["stream"] = True
        async with self._client._client() as c:  # pylint: disable=protected-access
            resp = await c.post(url, json=payload)
            if resp.status_code >= 400:
                raise APIError(resp.status_code, resp.text, body=await resp.aread())
            async for line in resp.aiter_lines():
                if not line:
                    continue
                yield StreamEvent(data=line)