from dataclasses import dataclass

from fastadmin import WidgetType


@dataclass
class ModelFieldWidgetSchema:
    """Orm model field schema"""

    name: str
    column_name: str
    is_m2m: bool
    is_pk: bool
    is_immutable: bool
    form_widget_type: WidgetType
    form_widget_props: dict
    filter_widget_type: WidgetType
    filter_widget_props: dict
