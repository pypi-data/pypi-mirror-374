from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel, JsonValue

T = TypeVar("T")


class BddFileResponse(BaseModel, Generic[T]):
    code: int
    data: T | None
    message: str | None


class BddFilePaged(BaseModel, Generic[T]):
    total: int
    items: list[T]


class Biz(str, Enum):
    chat = "chat"
    knowledge_base = "knowledgeBase"
    zero2x = "zero2x"


class FileStatus(str, Enum):
    ok = "ok"
    uploading = "uploading"
    merging = "merging"
    error = "error"


class UploadParams(BaseModel):
    filename: str
    biz: Biz
    biz_params: JsonValue


class FileInfo(BaseModel):
    id: int
    filename: str
    size: int
    hashcode: str
    upload_at: datetime
    user_id: str
    status: FileStatus
    biz: Biz
    biz_params: JsonValue


class SyncChatFileToLocalResult(BaseModel):
    is_success: bool
    file_info: FileInfo
    local_path: Path
    error_message: str | None


class SyncChatFileToRemoteStatus(str, Enum):
    success = "success"
    failed = "failed"
    skipped = "skipped"


class SyncChatFileToRemoteResult(BaseModel):
    status: SyncChatFileToRemoteStatus
    file_id: int | None
    error_message: str | None


class MultipartUploadFileStatus(BaseModel):
    file_id: int
    status: FileStatus
    part_size: int
    uploaded_parts: list[int] | None
    remaining_parts: list[int] | None


class DirectorySortBy(str, Enum):
    name_asc = "name_asc"
    name_desc = "name_desc"
    created_at_asc = "created_at_asc"
    created_at_desc = "created_at_desc"


class DirectoryInfo(BaseModel):
    id: int
    created_at: datetime
    name: str


class FileSortBy(str, Enum):
    name_asc = "name_asc"
    name_desc = "name_desc"
    upload_at_asc = "upload_at_asc"
    upload_at_desc = "upload_at_desc"
