from fastadmin import WidgetType, register

from src.adapters.database.models import Manager
from src.adapters.database.repositories import ManagerRepository
from src.admin.override_fastadmin import CustomModelAdmin
from src.schemas.admin.manager import (
    ManagersCreate,
    ManagersUpdate,
    ManagersGet,
    ManagersList,
)


@register(Manager)
class ManagerAdmin(CustomModelAdmin):
    Manager.__name__ = verbose_name = verbose_name_plural = "Менеджеры"

    schemaCreate = ManagersCreate
    schemaUpdate = ManagersUpdate
    schemaGet = ManagersGet
    schemaList = ManagersList

    model_repository = ManagerRepository

    list_display = ("phone", "first_name", "second_name")
    list_display_links = ("phone",)
    list_filter = ("phone", "first_name", "second_name")

    search_fields = (
        "first_name",
        "second_name",
        "phone",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "role",
                    "first_name",
                    "second_name",
                    "email",
                    "phone",
                    "password",
                )
            },
        ),
    )
    formfield_overrides = {  # noqa: RUF012
        "role": (
            WidgetType.Select,
            {
                "required": True,
                "options": [
                    {"label": "менеджер", "value": 0},
                    {"label": "главный менеджер", "value": 1},
                    {"label": "админ", "value": 2},
                ],
            },
        ),
        "first_name": (WidgetType.Input, {"required": True}),
        "second_name": (WidgetType.Input, {"required": True}),
        "email": (WidgetType.EmailInput, {"required": True}),
        "phone": (WidgetType.PhoneInput, {"required": True}),
        "password": (WidgetType.PasswordInput, {"passwordModalForm": True}),
    }
