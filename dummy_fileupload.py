from io import BytesIO
from typing import Protocol


BUCKET_NAME = "upload-bucket"


class AbstractStorageProvider(Protocol):
    def upload(
        self, bucket: str, file_name: str, content_type: str
    ) -> None: ...

    def download(self, bucket: str, file_name: str) -> BytesIO: ...


class S3StorageProvider(AbstractStorageProvider):
    def __init__(self) -> None:
        import boto3

        self.client = boto3.client("s3")

    def upload(self, bucket: str, file_name: str, content_type: str) -> None:
        self.client.upload_file(
            file_name,
            bucket,
            file_name,
            ExtraArgs={"ContentType": content_type},
        )

    def download(self, bucket: str, file_name: str) -> BytesIO:
        self.client.download_file(
            Bucket=bucket, Key=file_name, Filename=f"/tmp/{file_name}"
        )
        with open(f"/tmp/{file_name}", "rb") as f:
            return BytesIO(f.read())


class UnhandledContentType(Exception):
    pass


class AbstractFileUploadHander(Protocol):
    def handle_upload(self, file_name: str, content_type: str) -> None: ...


class ImageUploadHandler(AbstractFileUploadHander):
    def __init__(self, storage_provider: AbstractStorageProvider):
        self.storage_provider = storage_provider

    def handle_upload(self, file_name: str, content_type: str) -> None:
        pass


class VideoUploadHandler(AbstractFileUploadHander):

    def __init__(self, storage_provider: AbstractStorageProvider):
        self.storage_provider = storage_provider

    def handle_upload(self, file_name: str, content_type: str) -> None:
        pass


class PdfUploadHandler(AbstractFileUploadHander):

    def __init__(self, storage_provider: AbstractStorageProvider):
        self.storage_provider = storage_provider

    def handle_upload(self, file_name: str, content_type: str) -> None:
        self.storage_provider.upload(BUCKET_NAME, file_name, content_type)


def upload_handler_factory(
    content_type: str, storage_provider: AbstractStorageProvider
) -> AbstractFileUploadHander:
    if content_type.startswith("image/"):
        return ImageUploadHandler(storage_provider)
    elif content_type.startswith("video/"):
        return VideoUploadHandler(storage_provider)
    elif content_type == "application/pdf":
        return PdfUploadHandler(storage_provider)
    else:
        raise UnhandledContentType(f"Unsupported content type: {content_type}")


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    file_name = args[0]
    content_type = args[1]
    s3_provider = S3StorageProvider()

    try:
        handler = upload_handler_factory(content_type, s3_provider)
    except UnhandledContentType as e:
        print(e)
        sys.exit(1)

    handler.handle_upload(file_name, content_type)
