from typing import Any

from pydantic import BaseModel, ConfigDict


class ContentParameter(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    column_name: str = "images"
    content_repository: Any
    image_field_name: str = "uri"
    relation_id_field_name: str
    extra_payload_fields: dict[str, Any] = dict()
    image_type: bool = True
