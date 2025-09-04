import random
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Generator

import pytest

from bdd_file import BddFileClient


@pytest.fixture(scope="module")
def bdd_file_client() -> BddFileClient:
    client = BddFileClient(default_user_id="114514")
    return client


@pytest.fixture(scope="module")
def large_file() -> Generator[Path, None, None]:
    size = 13 * 1024 * 1024
    with NamedTemporaryFile(delete=False) as temp_file:
        chunk_size = 1024 * 1024
        offset = 0
        while offset < size:
            chunk_size = min(chunk_size, size - offset)
            temp_file.write(random.randbytes(chunk_size))
            offset += chunk_size

        temp_file.close()

        yield Path(temp_file.name)


def test_multipart_upload(bdd_file_client: BddFileClient, large_file: Path):
    result = bdd_file_client.upload(path=large_file, mode="multipart", biz="chat", biz_params={"chat_id": "191810"})
    assert result is not None

    bdd_file_client.delete(file_id=result, user_id="114514")
