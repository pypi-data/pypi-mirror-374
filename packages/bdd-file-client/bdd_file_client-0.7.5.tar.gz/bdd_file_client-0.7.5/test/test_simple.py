from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Generator
from uuid import uuid4

import pytest
import requests

from bdd_file import BddFileClient, BddFileError
from bdd_file.models import SyncChatFileToRemoteStatus


@pytest.fixture(scope="module")
def bdd_file_client() -> BddFileClient:
    return BddFileClient(default_user_id="114514")


@pytest.fixture(scope="function")
def upload_file_only(bdd_file_client: BddFileClient) -> int:
    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"test")
        temp_file.close()

        result = bdd_file_client.upload(
            path=temp_file.name, mode="simple", biz="chat", biz_params={"chat_id": "191810"}
        )
        assert result is not None

    return result


@pytest.fixture(scope="function")
def upload_file(bdd_file_client: BddFileClient, upload_file_only: int) -> Generator[int, None, None]:
    yield upload_file_only
    bdd_file_client.delete(file_id=upload_file_only)


def test_download_file(bdd_file_client: BddFileClient, upload_file: int):
    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file.close()

        bdd_file_client.download(file_id=upload_file, path=temp_file.name)
        with open(temp_file.name, "rb") as f:
            assert f.read() == b"test"


def test_get_download_url(bdd_file_client: BddFileClient, upload_file: int):
    url = bdd_file_client.get_download_url(file_id=upload_file)
    assert url is not None
    assert isinstance(url, str)
    assert url.startswith("http")

    with requests.get(url) as response:
        assert response.status_code == 200
        assert response.content == b"test"


def test_delete_file(bdd_file_client: BddFileClient, upload_file_only: int):
    bdd_file_client.delete(file_id=upload_file_only)

    with pytest.raises(BddFileError):
        bdd_file_client.download(file_id=upload_file_only)


def test_list_chat_files(bdd_file_client: BddFileClient, upload_file: int):
    result = bdd_file_client.list_chat_files(chat_id="191810")
    assert result is not None
    assert upload_file in [item.id for item in result]


def test_sync_chat_files_to_local(bdd_file_client: BddFileClient, upload_file: int):
    with TemporaryDirectory() as temp_dir:
        result = bdd_file_client.sync_chat_files_to_local(chat_id="191810", local_dir=temp_dir)
        assert len(result) > 0
        assert all(result[file_id].is_success for file_id in result)
        assert upload_file in result.keys()


def test_sync_chat_files_to_remote(bdd_file_client: BddFileClient):
    with TemporaryDirectory() as temp_dir:
        filename = f"test_{uuid4().hex}.txt"
        Path(temp_dir).joinpath(filename).write_text("test")
        result = bdd_file_client.sync_chat_files_to_remote(chat_id="191810", local_dir=temp_dir)
        assert len(result) > 0
        for file, result in result.items():
            assert result.status != SyncChatFileToRemoteStatus.failed
            if file.name == filename:
                assert result.status == SyncChatFileToRemoteStatus.success
            else:
                assert result.status == SyncChatFileToRemoteStatus.skipped
