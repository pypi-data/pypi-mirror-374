from __future__ import annotations
from typing import Any, Optional, AsyncIterator
import httpx

from nlbone.core.ports.files import AsyncFileServicePort
from nlbone.config.settings import get_settings
from .uploadchi import UploadchiError, _auth_headers, _build_list_query, _filename_from_cd, _resolve_token

class UploadchiAsyncClient(AsyncFileServicePort):
    def __init__(self, base_url: Optional[str] = None, timeout_seconds: Optional[float] = None, client: httpx.AsyncClient | None = None) -> None:
        s = get_settings()
        self._base_url = base_url or str(s.UPLOADCHI_BASE_URL)
        self._timeout = timeout_seconds or float(s.HTTP_TIMEOUT_SECONDS)
        self._client = client or httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout, follow_redirects=True)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def upload_file(self, file_bytes: bytes, filename: str, params: dict[str, Any] | None = None, token: str | None = None) -> dict:
        tok = _resolve_token(token)
        files = {"file": (filename, file_bytes)}
        data = (params or {}).copy()
        r = await self._client.post("", files=files, data=data, headers=_auth_headers(tok))
        if r.status_code >= 400:
            raise UploadchiError(r.status_code, await r.aread())
        return r.json()

    async def commit_file(self, file_id: int, client_id: str, token: str | None = None) -> None:
        tok = _resolve_token(token)
        r = await self._client.post(f"/{file_id}/commit", headers=_auth_headers(tok), params={"client_id": client_id} if client_id else None)
        if r.status_code not in (204, 200):
            raise UploadchiError(r.status_code, await r.aread())

    async def list_files(self, limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None, sort: list[tuple[str, str]] | None = None, token: str | None = None) -> dict:
        tok = _resolve_token(token)
        q = _build_list_query(limit, offset, filters, sort)
        r = await self._client.get("", params=q, headers=_auth_headers(tok))
        if r.status_code >= 400:
            raise UploadchiError(r.status_code, await r.aread())
        return r.json()

    async def get_file(self, file_id: int, token: str | None = None) -> dict:
        tok = _resolve_token(token)
        r = await self._client.get(f"/{file_id}", headers=_auth_headers(tok))
        if r.status_code >= 400:
            raise UploadchiError(r.status_code, await r.aread())
        return r.json()

    async def download_file(self, file_id: int, token: str | None = None) -> tuple[AsyncIterator[bytes], str, str]:
        tok = _resolve_token(token)
        r = await self._client.get(f"/{file_id}/download", headers=_auth_headers(tok), stream=True)
        if r.status_code >= 400:
            body = await r.aread()
            raise UploadchiError(r.status_code, body.decode(errors="ignore"))
        filename = _filename_from_cd(r.headers.get("content-disposition"), fallback=f"file-{file_id}")
        media_type = r.headers.get("content-type", "application/octet-stream")

        async def _aiter() -> AsyncIterator[bytes]:
            try:
                async for chunk in r.aiter_bytes():
                    yield chunk
            finally:
                await r.aclose()

        return _aiter(), filename, media_type

    async def delete_file(self, file_id: int, token: str | None = None) -> None:
        tok = _resolve_token(token)
        r = await self._client.delete(f"/{file_id}", headers=_auth_headers(tok))
        if r.status_code not in (204, 200):
            body = await r.aread()
            raise UploadchiError(r.status_code, body.decode(errors="ignore"))
