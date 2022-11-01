import os
from pathlib import Path
from tempfile import TemporaryDirectory, NamedTemporaryFile

import pytest

from common.file_system.local_file_system import LocalFileSystem


@pytest.fixture(scope="function")
def local_fs():
    temp_dir = TemporaryDirectory()
    temp_dir_path = Path(temp_dir.name)
    yield LocalFileSystem(temp_dir_path)
    temp_dir.cleanup()


def test_adds_file(local_fs):
    file_content = b"test"
    local_fs.add("test.txt", file_content)

    with open(local_fs._directory / "test.txt", mode="rb") as file:
        assert file.read() == file_content


def test_get_by_name(local_fs):
    file_content = b"test"
    name = "test.txt"
    with open(local_fs._directory / name, mode="wb") as file:
        file.write(file_content)

    assert local_fs.get_by_name(name) == file_content


def test_get_by_name_raises_file_not_found_if_no_file_exists(local_fs):
    name = "test.txt"
    with pytest.raises(FileNotFoundError):
        local_fs.get_by_name(name)


def test_list(local_fs):
    sorted_names = ["1.txt", "2.txt", "3.txt"]
    content = b"vodichka"
    for name in sorted_names:
        with open(local_fs._directory / name, mode="wb") as file:
            file.write(content)

    assert local_fs.list() == sorted_names


def test_delete(local_fs):
    file_content = b"test"
    name = "test.txt"
    with open(local_fs._directory / name, mode="wb") as file:
        file.write(file_content)

    local_fs.delete(name)

    assert os.listdir(local_fs._directory) == []


def test_upload(local_fs):
    content = b"chess.c*m"
    upload_name = "test.txt"

    with NamedTemporaryFile(delete=True) as file:
        with open(file.name, mode="wb") as write_to:
            write_to.write(content)

        file_path = Path(file.name)
        local_fs.upload(name=upload_name, file_path=file_path)

    with open(local_fs._directory / upload_name, mode="rb") as file:
        assert file.read() == content


def test_download(local_fs):
    content = b"chess.c*m"
    uploaded_name = "test.txt"

    with open(local_fs._directory / uploaded_name, mode="wb") as file:
        file.write(content)

    with NamedTemporaryFile(delete=True) as file:
        local_fs.download(uploaded_name, Path(file.name))

        with open(file.name, mode="rb") as read_from:
            assert read_from.read() == content
