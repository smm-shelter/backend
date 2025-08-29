from fastadmin import WidgetType, register

from src.adapters.database.models import PetType
from src.adapters.database.repositories import PetTypeRepository
from src.admin.override_fastadmin import CustomModelAdmin
from src.schemas.admin.pet_type import (
    PetTypeCreate,
    PetTypeUpdate,
    PetTypeGet,
    PetTypeList,
)


@register(PetType)
class PetTypeAdmin(CustomModelAdmin):
    PetType.__name__ = verbose_name = verbose_name_plural = "Типы питомцев"
    
    schemaCreate = PetTypeCreate
    schemaUpdate = PetTypeUpdate
    schemaGet = PetTypeGet
    schemaList = PetTypeList

    model_repository = PetTypeRepository

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
