from __future__ import annotations

import json
from typing import Any, AsyncIterator, Optional

import httpx

from nlbone.core.ports.files import FileServicePort
from nlbone.config.settings import get_settings


class FileServiceException(RuntimeError):
    def __init__(self, status: int, detail: Any | None = None):
        super().__init__(f"Uploadchi HTTP {status}: {detail}")
        self.status = status
        self.detail = detail


def _auth_headers(token: str | None) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"} if token else {}


def _build_list_query(
        limit: int,
        offset: int,
        filters: dict[str, Any] | None,
        sort: list[tuple[str, str]] | None,
) -> dict[str, Any]:
    q: dict[str, Any] = {"limit": limit, "offset": offset}
    if filters:
        # سرور شما `filters` را به صورت string می‌گیرد؛
        # اگر سمت سرور JSON هم قبول می‌کند، این بهتر است:
        q["filters"] = json.dumps(filters)
    if sort:
        # "created_at:desc,id:asc"
        q["sort"] = ",".join([f"{f}:{o}" for f, o in sort])
    return q


class UploadchiClient(FileServicePort):
    """
    httpx-based client for the Uploadchi microservice.

    Base URL نمونه: http://uploadchi.internal/api/v1/files
    """

    def __init__(
            self,
            base_url: Optional[str] = None,
            timeout_seconds: Optional[float] = None,
            client: httpx.AsyncClient | None = None,
    ) -> None:
        s = get_settings()
        self._base_url = base_url or str(s.UPLOADCHI_BASE_URL)
        self._timeout = timeout_seconds or float(s.HTTP_TIMEOUT_SECONDS)
        # اگر کلاینت تزریق نشد، خودمان می‌سازیم
        self._client = client or httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            follow_redirects=True,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    # ---------- Endpoints ----------

    async def upload_file(
            self,
            file_bytes: bytes,
            filename: str,
            params: dict[str, Any] | None = None,
            token: str | None = None,
    ) -> dict:
        """
        POST ""  →  returns FileOut (dict)
        fields:
          - file: Upload (multipart)
          - other params (e.g., bucket, folder, content_type, ...)
        """
        files = {"file": (filename, file_bytes)}
        data = (params or {}).copy()
        r = await self._client.post(
            url="",
            files=files,
            data=data,
            headers=_auth_headers(token),
        )
        if r.status_code >= 400:
            raise FileServiceException(r.status_code, r.text)
        return r.json()

    async def commit_file(
            self,
            file_id: int,
            client_id: str,
            token: str | None = None,
    ) -> None:
        """
        POST "/{file_id}/commit" 204
        """
        r = await self._client.post(
            f"/{file_id}/commit",
            headers=_auth_headers(token),
            params={"client_id": client_id} if client_id else None,
        )
        if r.status_code not in (204, 200):
            raise FileServiceException(r.status_code, r.text)

    async def list_files(
            self,
            limit: int = 10,
            offset: int = 0,
            filters: dict[str, Any] | None = None,
            sort: list[tuple[str, str]] | None = None,
            token: str | None = None,
    ) -> dict:
        """
        GET "" → returns PaginateResponse-like dict
          { "data": [...], "total_count": int | null, "total_page": int | null }
        """
        q = _build_list_query(limit, offset, filters, sort)
        r = await self._client.get("", params=q, headers=_auth_headers(token))
        if r.status_code >= 400:
            raise FileServiceException(r.status_code, r.text)
        return r.json()

    async def get_file(
            self,
            file_id: int,
            token: str | None = None,
    ) -> dict:
        """
        GET "/{file_id}" → FileOut dict
        """
        r = await self._client.get(f"/{file_id}", headers=_auth_headers(token))
        if r.status_code >= 400:
            raise FileServiceException(r.status_code, r.text)
        return r.json()

    async def download_file(
            self,
            file_id: int,
            token: str | None = None,
    ) -> tuple[AsyncIterator[bytes], str, str]:
        """
        GET "/{file_id}/download" → stream + headers (filename, content-type)
        """
        r = await self._client.get(f"/{file_id}/download", headers=_auth_headers(token))
        if r.status_code >= 400:
            text = await r.aread()
            raise FileServiceException(r.status_code, text.decode(errors="ignore"))

        disp = r.headers.get("content-disposition", "")
        filename = (
            disp.split("filename=", 1)[1].strip("\"'") if "filename=" in disp else f"file-{file_id}"
        )
        media_type = r.headers.get("content-type", "application/octet-stream")

        async def _aiter() -> AsyncIterator[bytes]:
            async for chunk in r.aiter_bytes():
                yield chunk
            await r.aclose()

        return _aiter(), filename, media_type

    async def delete_file(
            self,
            file_id: int,
            token: str | None = None,
    ) -> None:
        """
        DELETE "/{file_id}" → 204
        """
        r = await self._client.delete(f"/{file_id}", headers=_auth_headers(token))
        if r.status_code not in (204, 200):
            raise FileServiceException(r.status_code, r.text)
