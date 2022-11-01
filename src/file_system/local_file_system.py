import os
from pathlib import Path
from typing import List

from file_system.abstract_file_system import AbstractFileSystem


class LocalFileSystem(AbstractFileSystem):
    def __init__(self, directory: Path):
        self._directory = directory

    def get_by_name(self, name: str) -> bytes:
        file_path = self._directory / name
        if file_path.exists():
            with open(file_path, "rb") as file:
                return file.read()
        raise FileNotFoundError(f"File {str(file_path)} not found")

    def add(self, name: str, content: bytes):
        with open(self._directory / name, mode="wb") as file:
            file.write(content)

    def list(self) -> List[str]:
        return sorted(os.listdir(self._directory))

    def delete(self, name: str):
        os.remove(self._directory / name)

    def upload(self, name: str, file_path: Path):
        with open(self._directory / name, mode="wb") as target:
            with open(file_path, mode="rb") as source:
                content = source.read()
                target.write(content)

    def download(self, name: str, file_path: Path):
        with open(self._directory / name, mode="rb") as source:
            with open(file_path, mode="wb") as target:
                content = source.read()
                target.write(content)
