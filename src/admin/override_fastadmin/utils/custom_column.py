from enum import Enum
from typing import Any, Optional

from fastadmin import WidgetType
from pydantic import BaseModel, ConfigDict


class CustomColumn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    column_name: str
    join_field: Optional[Any] = None
    get_new_value: Any
    filter: dict[str, Any]
    sort_field: Optional[Any] = None
    widget_type: Enum = WidgetType.Input
