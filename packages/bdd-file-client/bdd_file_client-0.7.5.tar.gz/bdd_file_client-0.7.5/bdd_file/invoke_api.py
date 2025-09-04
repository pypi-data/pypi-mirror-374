import functools
import json
import math
from typing import IO, Callable, Type, TypeVar

import requests
from pydantic import JsonValue

from .exception import BddFileError
from .models import (
    BddFilePaged,
    BddFileResponse,
    Biz,
    DirectoryInfo,
    DirectorySortBy,
    FileInfo,
    FileSortBy,
    MultipartUploadFileStatus,
)

Data = TypeVar("Data")


def _invoke_api(
    api_name: str, response_type: Type[Data]
) -> Callable[[Callable[..., requests.Response]], Callable[..., Data]]:
    def wrapper(func: Callable[..., requests.Response]) -> Callable[..., Data]:
        @functools.wraps(func)
        def inner_wrapper(*args, **kwargs) -> Data:
            try:
                raw_response = func(*args, **kwargs)
            except Exception as e:
                raise BddFileError(f"{api_name}失败: {e}") from e

            if raw_response.status_code != 200:
                raise BddFileError(f"{api_name}失败: {raw_response.status_code} {raw_response.text}")

            response = BddFileResponse[response_type].model_validate_json(raw_response.text)
            if response.code != 0 or response.data is None:
                raise BddFileError(f"{api_name}失败: {response.message}")
            return response.data

        return inner_wrapper

    return wrapper


@_invoke_api("上传文件", int)
def upload_simple(
    serivce_url: str,
    stream: IO[bytes],
    filename: str,
    size: int,
    hashcode: str | None,
    user_id: str,
    biz: str,
    biz_params: JsonValue,
) -> requests.Response:
    params = json.dumps(
        {"filename": filename, "biz": Biz(biz).value, "biz_params": biz_params, "size": size, "hashcode": hashcode}
    )
    return requests.post(
        f"{serivce_url}/uploadSimpleFile",
        files={"file": (filename, stream, "application/octet-stream")},
        data={"params": params},
        headers={"X-User-Id": user_id},
    )


def upload_multipart(
    service_url: str,
    stream: IO[bytes],
    filename: str,
    size: int,
    hashcode: str | None,
    user_id: str,
    biz: str,
    biz_params: JsonValue,
) -> int:
    part_size = 5 * 1024 * 1024  # 5MB
    part_count = math.ceil(size / part_size)
    file_id = init_multipart_upload_file(service_url, filename, size, part_size, hashcode, user_id, biz, biz_params)
    for part_number in range(1, part_count + 1):
        part_stream = stream.read(part_size)
        upload_file_part(service_url, user_id, file_id, part_number, part_stream)
    complete_multipart_upload(service_url, user_id, file_id)
    return file_id


@_invoke_api("上传分片", int)
def init_multipart_upload_file(
    service_url: str,
    filename: str,
    size: int,
    part_size: int,
    hashcode: str | None,
    user_id: str,
    biz: str,
    biz_params: JsonValue,
) -> requests.Response:
    return requests.post(
        f"{service_url}/initMultipartUploadFile",
        json={
            "filename": filename,
            "size": size,
            "part_size": part_size,
            "hashcode": hashcode,
            "biz": Biz(biz).value,
            "biz_params": biz_params,
        },
        headers={"X-User-Id": user_id},
    )


@_invoke_api("上传分片", int)
def upload_file_part(
    service_url: str, user_id: str, file_id: int, part_number: int, stream: IO[bytes]
) -> requests.Response:
    return requests.post(
        f"{service_url}/uploadFilePart",
        files={"part": (f"part_{part_number}", stream, "application/octet-stream")},
        data={"params": json.dumps({"file_id": file_id, "part_number": part_number})},
        headers={"X-User-Id": user_id},
    )


@_invoke_api("完成分片上传", int)
def complete_multipart_upload(service_url: str, user_id: str, file_id: int) -> requests.Response:
    return requests.post(
        f"{service_url}/completeMultipartUpload", json={"file_id": file_id}, headers={"X-User-Id": user_id}
    )


@_invoke_api("取消分片上传", int)
def abort_multipart_upload(service_url: str, user_id: str, file_id: int) -> requests.Response:
    return requests.post(
        f"{service_url}/abortMultipartUpload", json={"file_id": file_id}, headers={"X-User-Id": user_id}
    )


@_invoke_api("获取分片上传文件状态", MultipartUploadFileStatus)
def get_multipart_upload_file_status(service_url: str, user_id: str, file_id: int) -> requests.Response:
    return requests.get(
        f"{service_url}/getMultipartUploadFileStatus", params={"file_id": file_id}, headers={"X-User-Id": user_id}
    )


def download(service_url: str, file_id: int, user_id: str, stream: IO[bytes]) -> None:
    try:
        raw_response = requests.get(
            f"{service_url}/downloadFile", params={"file_id": file_id}, headers={"X-User-Id": user_id}, stream=True
        )
    except Exception as e:
        raise BddFileError(f"下载文件失败: {e}") from e

    if raw_response.status_code != 200:
        raise BddFileError(f"下载文件失败: {raw_response.status_code} {raw_response.text}")

    for chunk in raw_response.iter_content(chunk_size=64 * 1024):
        stream.write(chunk)


@_invoke_api("获取下载URL", str)
def get_download_url(service_url: str, file_id: int, user_id: str, expires_seconds: int) -> requests.Response:
    return requests.get(
        f"{service_url}/getFileDownloadUrl",
        params={"file_id": file_id, "expires_in": expires_seconds},
        headers={"X-User-Id": user_id},
    )


@_invoke_api("删除文件", int)
def delete_file(service_url: str, file_id: int, user_id: str) -> requests.Response:
    return requests.delete(f"{service_url}/deleteFile", params={"file_id": file_id}, headers={"X-User-Id": user_id})


@_invoke_api("获取聊天文件列表", BddFilePaged[FileInfo])
def list_chat_files(service_url: str, chat_id: str, user_id: str, offset: int, limit: int) -> requests.Response:
    return requests.get(
        f"{service_url}/listChatFiles",
        params={"chat_id": chat_id, "offset": offset, "limit": limit},
        headers={"X-User-Id": user_id},
    )


@_invoke_api("获取目录列表", BddFilePaged[DirectoryInfo])
def list_directories(
    service_url: str, user_id: str, name: str | None, sort_by: DirectorySortBy | None, page_size: int, page_number: int
) -> requests.Response:
    return requests.get(
        f"{service_url}/listDirectories",
        params={"name": name, "sort_by": sort_by, "page_size": page_size, "page_number": page_number},
        headers={"X-User-Id": user_id},
    )


@_invoke_api("获取目录下的文件列表", BddFilePaged[FileInfo])
def list_files_in_directory(
    service_url: str,
    user_id: str,
    directory_id: int,
    name: str | None,
    sort_by: FileSortBy | None,
    page_size: int,
    page_number: int,
) -> requests.Response:
    return requests.get(
        f"{service_url}/listFilesInDirectory",
        params={
            "directory_id": directory_id,
            "name": name,
            "sort_by": sort_by,
            "page_size": page_size,
            "page_number": page_number,
        },
        headers={"X-User-Id": user_id},
    )
