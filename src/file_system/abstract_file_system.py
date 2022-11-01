from abc import ABC, abstractmethod
from pathlib import Path


class AbstractFileSystem(ABC):
    @abstractmethod
    def get_by_name(self, name: str) -> bytes:
        ...

    @abstractmethod
    def upload(self, name: str, file_path: Path):
        ...

    @abstractmethod
    def add(self, name: str, content: bytes):
        ...

    @abstractmethod
    def download(self, name: str, file_path: Path):
        ...

    @abstractmethod
    def list(self):
        ...

    @abstractmethod
    def delete(self, name: str):
        ...
