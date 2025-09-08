from __future__ import annotations
import json
from typing import Any, Optional
import httpx

from nlbone.core.ports.files import FileServicePort
from nlbone.config.settings import get_settings

class UploadchiError(RuntimeError):
    def __init__(self, status: int, detail: Any | None = None):
        super().__init__(f"Uploadchi HTTP {status}: {detail}")
        self.status = status
        self.detail = detail

def _resolve_token(explicit: str | None) -> str | None:
    if explicit is not None:
        return explicit
    s = get_settings()
    return s.UPLOADCHI_TOKEN.get_secret_value() if s.UPLOADCHI_TOKEN else None

def _auth_headers(token: str | None) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"} if token else {}

def _build_list_query(limit: int, offset: int, filters: dict[str, Any] | None, sort: list[tuple[str, str]] | None) -> dict[str, Any]:
    q: dict[str, Any] = {"limit": limit, "offset": offset}
    if filters:
        q["filters"] = json.dumps(filters)
    if sort:
        q["sort"] = ",".join([f"{f}:{o}" for f, o in sort])
    return q

def _filename_from_cd(cd: str | None, fallback: str) -> str:
    if not cd:
        return fallback
    if "filename=" in cd:
        return cd.split("filename=", 1)[1].strip("\"'")
    return fallback

class UploadchiClient(FileServicePort):
    def __init__(self, base_url: Optional[str] = None, timeout_seconds: Optional[float] = None, client: httpx.Client | None = None) -> None:
        s = get_settings()
        self._base_url = base_url or str(s.UPLOADCHI_BASE_URL)
        self._timeout = timeout_seconds or float(s.HTTP_TIMEOUT_SECONDS)
        self._client = client or httpx.Client(base_url=self._base_url, timeout=self._timeout, follow_redirects=True)

    def close(self) -> None:
        self._client.close()

    def upload_file(self, file_bytes: bytes, filename: str, params: dict[str, Any] | None = None, token: str | None = None) -> dict:
        tok = _resolve_token(token)
        files = {"file": (filename, file_bytes)}
        data = (params or {}).copy()
        r = self._client.post("", files=files, data=data, headers=_auth_headers(tok))
        if r.status_code >= 400:
            raise UploadchiError(r.status_code, r.text)
        return r.json()

    def commit_file(self, file_id: int, client_id: str, token: str | None = None) -> None:
        tok = _resolve_token(token)
        r = self._client.post(f"/{file_id}/commit", headers=_auth_headers(tok), params={"client_id": client_id} if client_id else None)
        if r.status_code not in (204, 200):
            raise UploadchiError(r.status_code, r.text)

    def list_files(self, limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None, sort: list[tuple[str, str]] | None = None, token: str | None = None) -> dict:
        tok = _resolve_token(token)
        q = _build_list_query(limit, offset, filters, sort)
        r = self._client.get("", params=q, headers=_auth_headers(tok))
        if r.status_code >= 400:
            raise UploadchiError(r.status_code, r.text)
        return r.json()

    def get_file(self, file_id: int, token: str | None = None) -> dict:
        tok = _resolve_token(token)
        r = self._client.get(f"/{file_id}", headers=_auth_headers(tok))
        if r.status_code >= 400:
            raise UploadchiError(r.status_code, r.text)
        return r.json()

    def download_file(self, file_id: int, token: str | None = None) -> tuple[bytes, str, str]:
        tok = _resolve_token(token)
        r = self._client.get(f"/{file_id}/download", headers=_auth_headers(tok))
        if r.status_code >= 400:
            raise UploadchiError(r.status_code, r.text)
        filename = _filename_from_cd(r.headers.get("content-disposition"), fallback=f"file-{file_id}")
        media_type = r.headers.get("content-type", "application/octet-stream")
        return r.content, filename, media_type

    def delete_file(self, file_id: int, token: str | None = None) -> None:
        tok = _resolve_token(token)
        r = self._client.delete(f"/{file_id}", headers=_auth_headers(tok))
        if r.status_code not in (204, 200):
            raise UploadchiError(r.status_code, r.text)
