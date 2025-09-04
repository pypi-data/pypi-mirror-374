from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from pathlib import Path
from typing import IO

from pydantic import JsonValue

from .exception import BddFileError
from .invoke_api import (
    delete_file,
    download,
    get_download_url,
    list_chat_files,
    list_directories,
    list_files_in_directory,
    upload_multipart,
    upload_simple,
)
from .models import (
    BddFilePaged,
    Biz,
    DirectoryInfo,
    DirectorySortBy,
    FileInfo,
    FileSortBy,
    SyncChatFileToLocalResult,
    SyncChatFileToRemoteResult,
    SyncChatFileToRemoteStatus,
)
from .settings import BDD_FILE_PROFILES, settings


class UploadMode(str, Enum):
    """
    上传模式

    SIMPLE: 简单上传，不支持断点续传
    MULTIPART: 分片上传，支持断点续传
    AUTO: 自动选择上传模式，如果文件大于 100MB，则使用分片上传，否则使用简单上传
    """

    SIMPLE = "simple"
    MULTIPART = "multipart"
    AUTO = "auto"


class BddFileClient:
    def __init__(
        self,
        profile: str = settings.PROFILE,
        default_user_id: str | None = None,
        default_biz: str | None = None,
        default_mode: UploadMode | None = None,
    ):
        self.service_url = BDD_FILE_PROFILES[profile]
        self.default_user_id = default_user_id
        self.default_biz = default_biz
        self.default_mode = default_mode

    def upload(
        self,
        *,
        path: str | Path | None = None,
        stream: IO[bytes] | None = None,
        filename: str | None = None,
        mode: UploadMode | str = UploadMode.AUTO,
        size: int | None = None,
        hashcode: str | None = None,
        user_id: str | None = None,
        biz: str | None = None,
        biz_params: JsonValue = None,
    ) -> int:
        """
        上传文件

        参数：
            - path: 文件路径，path 和 stream 只能传一个
            - stream: 文件流，path 和 stream 只能传一个
            - filename: 文件名，如果传了，则使用这个文件名，否则使用 path 的文件名；传 stream 时，filename 必须传
            - mode: 上传模式，默认使用 client 的 default_mode
            - size: 文件大小，如果传了 stream 则必须传，如果传了 path 则忽略该参数
            - hashcode: 文件哈希值，可选项
            - user_id: 用户ID，如果没有传，则使用 client 的 default_user_id
            - biz: 业务类型，如果没有传，则使用 client 的 default_biz
            - biz_params: 业务参数，JSON 格式

        返回：
            - 文件 ID
        """
        user_id = self._ensure_user_id(user_id)
        if biz is None:
            if self.default_biz is None:
                raise BddFileError("biz为空")
            biz = self.default_biz

        mode = UploadMode(mode)
        if stream is None and path is not None:
            path = Path(path)
            filename = filename or path.name
            size = path.stat().st_size
            with open(path, "rb") as f:
                return _invoke_upload(mode, self.service_url, f, filename, size, hashcode, user_id, biz, biz_params)
        elif stream is not None and path is None:
            if size is None:
                raise BddFileError("size为空")
            if filename is None:
                raise BddFileError("filename为空")
            return _invoke_upload(mode, self.service_url, stream, filename, size, hashcode, user_id, biz, biz_params)
        elif stream is None and path is None:
            raise BddFileError("path和stream不能同时为空")
        else:
            raise BddFileError("path和stream不能同时设置")

    def download(
        self,
        *,
        file_id: int,
        user_id: str | None = None,
        path: str | Path | None = None,
        stream: IO[bytes] | None = None,
    ) -> None:
        """
        下载文件

        参数：
            - file_id: 文件ID
            - user_id: 用户ID，如果没有传，则使用 client 的 default_user_id
            - path: 文件路径，如果传了，则将文件下载到这个路径，与 stream 只能传一个
            - stream: 文件流，如果传了，则将文件下载到这个流，与 path 只能传一个
        """
        user_id = self._ensure_user_id(user_id)

        if path is not None and stream is None:
            with open(path, "wb") as f:
                download(self.service_url, file_id, user_id, f)
        elif stream is not None and path is None:
            download(self.service_url, file_id, user_id, stream)
        elif stream is None and path is None:
            raise BddFileError("path和stream不能同时为空")
        else:
            raise BddFileError("path和stream不能同时设置")

    def get_download_url(self, *, file_id: int, user_id: str | None = None, expires_seconds: int = 10 * 60) -> str:
        """
        获取下载URL

        参数：
            - file_id: 文件ID
            - user_id: 用户ID，如果没有传，则使用 client 的 default_user_id
            - expires_seconds: 下载URL的过期时间，默认10分钟

        返回：
            - 下载链接
        """
        user_id = self._ensure_user_id(user_id)
        return get_download_url(self.service_url, file_id, user_id, expires_seconds)

    def delete(self, *, file_id: int, user_id: str | None = None) -> None:
        """
        删除文件

        参数：
            - file_id: 文件ID
            - user_id: 用户ID，如果没有传，则使用 client 的 default_user_id
        """
        user_id = self._ensure_user_id(user_id)
        delete_file(self.service_url, file_id, user_id)

    def list_chat_files(self, *, chat_id: str, user_id: str | None = None) -> list[FileInfo]:
        """
        获取聊天文件列表

        参数：
            - chat_id: 聊天ID
            - user_id: 用户ID，如果没有传，则使用 client 的 default_user_id

        返回：
            - 文件列表
        """
        user_id = self._ensure_user_id(user_id)

        offset = 0
        result = []
        while True:
            file_page = list_chat_files(self.service_url, chat_id, user_id, offset, 100)
            if len(file_page.items) == 0:
                break
            result.extend(file_page.items)
            offset += len(file_page.items)
            if offset >= file_page.total:
                break
        return result

    def sync_chat_files_to_local(
        self, *, chat_id: str, local_dir: str | Path, user_id: str | None = None
    ) -> dict[int, SyncChatFileToLocalResult]:
        """
        将聊天文件同步到本地，覆盖同名的本地文件

        参数：
            - chat_id: 聊天ID
            - local_dir: 本地目录
            - user_id: 用户ID，如果没有传，则使用 client 的 default_user_id

        返回：
            - 同步的文件列表
        """

        def download_file(file: FileInfo) -> tuple[int, SyncChatFileToLocalResult]:
            local_path = Path(local_dir) / file.filename
            result = SyncChatFileToLocalResult(
                is_success=False, file_info=file, local_path=local_path, error_message=None
            )
            try:
                self.download(file_id=file.id, user_id=user_id, path=local_path)
                result.is_success = True
            except Exception as e:
                result.error_message = str(e)
            return file.id, result

        user_id = self._ensure_user_id(user_id)
        files = self.list_chat_files(chat_id=chat_id, user_id=user_id)
        with ThreadPoolExecutor() as executor:
            return dict(executor.map(download_file, files))

    def sync_chat_files_to_remote(
        self, *, chat_id: str, local_dir: str | Path, user_id: str | None = None
    ) -> dict[Path, SyncChatFileToRemoteResult]:
        """
        将聊天文件同步到远程，根据文件名判断是否需要同步
        1. 本地和远程都存在，跳过
        2. 本地存在，远程不存在，上传
        3. 本地不存在，远程存在，跳过

        参数：
            - chat_id: 聊天ID
            - local_dir: 本地目录
            - user_id: 用户ID，如果没有传，则使用 client 的 default_user_id

        返回：
            - 同步的文件列表
        """
        local_dir = Path(local_dir)
        local_files = {file for file in local_dir.rglob("*") if file.is_file()}
        remote_filenames = {file_info.filename for file_info in self.list_chat_files(chat_id=chat_id, user_id=user_id)}
        upload_files = {file for file in local_files if file.name not in remote_filenames}

        def upload_file(file: Path) -> tuple[Path, SyncChatFileToRemoteResult]:
            if file not in upload_files:
                return file, SyncChatFileToRemoteResult(
                    status=SyncChatFileToRemoteStatus.skipped, file_id=None, error_message=None
                )
            try:
                file_id = self.upload(path=file, user_id=user_id, biz=Biz.chat, biz_params={"chat_id": chat_id})
                return file, SyncChatFileToRemoteResult(
                    status=SyncChatFileToRemoteStatus.success, file_id=file_id, error_message=None
                )
            except Exception as e:
                return file, SyncChatFileToRemoteResult(
                    status=SyncChatFileToRemoteStatus.failed, file_id=None, error_message=str(e)
                )

        with ThreadPoolExecutor() as executor:
            return dict(executor.map(upload_file, local_files))

    def list_directories(
        self,
        *,
        user_id: str | None = None,
        name: str | None = None,
        sort_by: DirectorySortBy | None = None,
        page_size: int = 10,
        page_number: int = 1,
    ) -> BddFilePaged[DirectoryInfo]:
        user_id = self._ensure_user_id(user_id)
        return list_directories(self.service_url, user_id, name, sort_by, page_size, page_number)

    def _ensure_user_id(self, user_id: str | None) -> str:
        if user_id is None:
            if self.default_user_id is None:
                raise BddFileError("user_id为空")
            return self.default_user_id
        return user_id

    def list_files_in_directory(
        self,
        *,
        directory_id: int,
        user_id: str | None = None,
        name: str | None = None,
        sort_by: FileSortBy | None = None,
        page_size: int = 10,
        page_number: int = 1,
    ) -> BddFilePaged[FileInfo]:
        user_id = self._ensure_user_id(user_id)
        return list_files_in_directory(self.service_url, user_id, directory_id, name, sort_by, page_size, page_number)


def _invoke_upload(
    mode: UploadMode,
    service_url: str,
    stream: IO[bytes],
    filename: str,
    size: int,
    hashcode: str | None,
    user_id: str,
    biz: str,
    biz_params: JsonValue,
) -> int:
    if mode == UploadMode.SIMPLE:
        return upload_simple(service_url, stream, filename, size, hashcode, user_id, biz, biz_params)
    elif mode == UploadMode.MULTIPART:
        return upload_multipart(service_url, stream, filename, size, hashcode, user_id, biz, biz_params)
    if size > 100 * 1024 * 1024:
        return upload_multipart(service_url, stream, filename, size, hashcode, user_id, biz, biz_params)
    return upload_simple(service_url, stream, filename, size, hashcode, user_id, biz, biz_params)
