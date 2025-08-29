from fastadmin import WidgetType, register

from src.adapters.database.models import News
from src.adapters.database.repositories import NewsRepository, NewsContentRepository
from src.admin.override_fastadmin import CustomModelAdmin, ContentParameter
from src.schemas.admin.news import (
    NewsCreate,
    NewsUpdate,
    NewsGet,
    NewsList,
)


@register(News)
class NewsAdmin(CustomModelAdmin):
    News.__name__ = verbose_name = verbose_name_plural = "Новости"
    
    schemaCreate = NewsCreate
    schemaUpdate = NewsUpdate
    schemaGet = NewsGet
    schemaList = NewsList
    
    content_parameters = [
        ContentParameter(
            content_repository=NewsContentRepository,
            relation_id_field_name="news_id",
        )
    ]


    model_repository = NewsRepository

    list_display = ("title", "text", "publish_date")
    list_display_links = ("title",)
    list_filter = ("title", "text", "publish_date")

    search_fields = (
        "title",
        "text",
    )
    
    readonly_fields = ("publish_date",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "text",
                    "publish_date",
                    "images",
                )
            },
        ),
    )
    formfield_overrides = {  # noqa: RUF012
        "title": (WidgetType.Input, {"required": True}),
        "text": (WidgetType.RichTextArea, {"required": True}),
        "images": (WidgetType.Upload, {"required": False, "multiple": True}),
    }
