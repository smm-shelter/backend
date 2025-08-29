from abc import abstractmethod
from typing import BinaryIO, Protocol


class FileStorageProtocol(Protocol):
    @abstractmethod
    async def upload_file(
        self, file: BinaryIO, mimetype: str, new_filename: str | None = None
    ) -> str:
        """Uploads file to S3 storage returns new filename"""
        raise NotImplementedError

    @abstractmethod
    async def check_object_exists(self, key: str):
        """check file existence in S3 storage"""
        raise NotImplementedError

    @abstractmethod
    async def delete_file(self, filename: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_file_url(self, filename: str) -> str:
        raise NotImplementedError
