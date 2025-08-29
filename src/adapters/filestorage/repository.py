import mimetypes
from typing import BinaryIO
from uuid import uuid4

import botocore.exceptions
from aioboto3 import Session

from src.settings import settings
from src.utils.filestorage import FileStorageProtocol


class FileStorageRepository(FileStorageProtocol):
    def __init__(self, session: Session, settings=settings) -> None:
        self.session = session

        self.bucket_name = settings.S3_BUCKET_NAME
        self.api_url = settings.s3_url
        self.access_key = settings.S3_ACCESS_KEY
        self.secret_key = settings.S3_SECRET_KEY
        self.resource_url = settings.s3_resource_url

    async def upload_file(
        self, file: BinaryIO, mimetype: str, new_filename: str | None = None
    ) -> str:
        async with self.session.resource(
            service_name="s3",
            endpoint_url=settings.s3_url,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        ) as resource:
            self.bucket = await resource.Bucket(settings.S3_BUCKET_NAME)

            if new_filename is None:
                new_filename = await self._generate_new_filename(
                    mimetypes.guess_extension(mimetype)
                )

            await self.bucket.upload_fileobj(
                file,
                new_filename,
                ExtraArgs={
                    "ContentType": mimetype,
                    "ACL": "public-read",
                },
            )
        return new_filename

    async def _generate_new_filename(self, suffix: str | None) -> str:
        if suffix is None:
            suffix = ""
        filename = f"{uuid4().hex}{suffix}"
        while await self._check_object_exists(filename):
            filename = f"{uuid4().hex}{suffix}"
        return filename

    async def _check_object_exists(self, key: str):
        try:
            await (await self.bucket.Object(key)).load()
        except botocore.exceptions.ClientError as err:
            if err.response["Error"]["Code"] == "404":  # type: ignore
                return False
            raise err
        return True

    async def delete_file(self, filename: str):
        async with self.session.resource(
            service_name="s3",
            endpoint_url=settings.s3_url,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        ) as resource:
            self.bucket = await resource.Bucket(settings.S3_BUCKET_NAME)
            await (await self.bucket.Object(filename)).delete()

    def get_file_url(self, filename: str) -> str:
        return f"{self.resource_url}/{filename}"

    async def check_object_exists(self, key: str):
        async with self.session.resource(
            service_name="s3",
            endpoint_url=settings.s3_url,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        ) as resource:
            self.bucket = await resource.Bucket(settings.S3_BUCKET_NAME)
            try:
                await (await self.bucket.Object(key)).load()
            except botocore.exceptions.ClientError as err:
                if err.response["Error"]["Code"] == "404":  # type: ignore
                    return False
                raise err
            return True
