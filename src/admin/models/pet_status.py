from fastadmin import WidgetType, register

from src.adapters.database.models import PetStatus
from src.adapters.database.repositories import PetStatusRepository
from src.admin.override_fastadmin import CustomModelAdmin
from src.schemas.admin.pet_status import (
    PetStatusCreate,
    PetStatusUpdate,
    PetStatusGet,
    PetStatusList,
)


@register(PetStatus)
class PetStatusAdmin(CustomModelAdmin):
    PetStatus.__name__ = verbose_name = verbose_name_plural = "Статусы питомцев"
    
    schemaCreate = PetStatusCreate
    schemaUpdate = PetStatusUpdate
    schemaGet = PetStatusGet
    schemaList = PetStatusList

    model_repository = PetStatusRepository

    list_display = ("name",)
    list_display_links = ("name",)
    list_filter = ("name",)

    search_fields = (
        "name",
    )


    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                )
            },
        ),
    )
    formfield_overrides = {  # noqa: RUF012
        "name": (WidgetType.Input, {"required": True}),
    }
