from src.settings import settings


def get_file_url(filename: str) -> str:
    return f"{settings.s3_resource_url}/{filename}"
