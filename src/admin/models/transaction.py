from fastadmin import WidgetType, register

from src.adapters.database.models import Transaction
from src.adapters.database.repositories import TransactionRepository, TransactionContentRepository
from src.admin.override_fastadmin import CustomModelAdmin, ContentParameter
from src.schemas.admin.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionGet,
    TransactionList,
)


@register(Transaction)
class TransactionAdmin(CustomModelAdmin):
    Transaction.__name__ = verbose_name = verbose_name_plural = "Транзакции"
    
    schemaCreate = TransactionCreate
    schemaUpdate = TransactionUpdate
    schemaGet = TransactionGet
    schemaList = TransactionList
    
    content_parameters = [
        ContentParameter(
            content_repository=TransactionContentRepository,
            relation_id_field_name="transaction_id",
        )
    ]


    model_repository = TransactionRepository

    list_display = (
        "incoming",
        "amount",
        "sender_receiver",
        "comment"
    )
    list_display_links = (
        "amount",
        "sender_receiver"
    )
    list_filter = (
        "incoming",
        "amount",
        "sender_receiver",
        "comment",
    )

    search_fields = (
        "amount",
        "sender_receiver",
        "comment"
    )
    
    readonly_fields = ("date_of_payment",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "date_of_payment",
                    "amount",
                    "incoming",
                    "sender_receiver",
                    "comment",
                    "images",
                )
            },
        ),
    )
    formfield_overrides = {  # noqa: RUF012
        "amount": (WidgetType.InputNumber, {"required": True}),
        "incoming": (WidgetType.Checkbox, {"required": False, "default": False}),
        "sender_receiver": (WidgetType.Input, {"required": False}),
        "comment": (WidgetType.RichTextArea, {"required": False}),
        "images": (WidgetType.Upload, {"required": False, "multiple": True}),
    }
