from typing import Any

from fastadmin.models.base import ModelAdmin
from fastadmin.models.helpers import getattrs
from fastadmin.models.schemas import ModelFieldWidgetSchema, WidgetType
from fastadmin.settings import settings
from sqlalchemy.inspection import inspect


class FastAdminMixin(ModelAdmin):
    @staticmethod
    def get_model_pk_name(orm_model_cls: Any) -> str:
        """This method is used to get model pk name.

        :return: A str.
        """
        return getattrs(
            orm_model_cls,
            "__table__.primary_key._autoincrement_column.name",
            default="id",
        )

    def get_model_fields_with_widget_types(
        self,
        with_m2m: bool | None = None,
        with_upload: bool | None = None,
    ) -> list[ModelFieldWidgetSchema]:
        """This method is used to get model fields with widget types.

        :params with_m2m: a flag to include m2m fields.
        :params with_upload: a flag to include upload fields.
        :return: A list of ModelFieldWidgetSchema.
        """
        mapper = inspect(self.model_cls)
        orm_model_fields = [f for f in mapper.c if not f.foreign_keys] + list(
            mapper.relationships
        )

        fields = []
        for orm_model_field in orm_model_fields:
            field_type = getattrs(orm_model_field, "direction.name") or getattrs(
                orm_model_field, "type.__class__.__name__"
            )
            field_name = orm_model_field.key
            column_name = orm_model_field.key

            if field_type in ("ONETOMANY",):
                continue

            if field_type in (
                "ONETOONE",
                "MANYTOONE",
            ) and not column_name.endswith("_id"):
                column_name = f"{column_name}_id"

                if column_name not in [f.key for f in mapper.c if f.foreign_keys]:
                    continue

            is_m2m = field_type == "MANYTOMANY"
            w_type, _ = self.formfield_overrides.get(field_name, (None, None))
            is_upload = w_type == WidgetType.Upload
            if with_m2m is not None and not with_m2m and is_m2m:
                continue
            if with_m2m is not None and with_m2m and not is_m2m:
                continue
            if with_upload is not None and not with_upload and is_upload:
                continue
            if with_upload is not None and with_upload and not is_upload:
                continue

            is_pk = self.get_model_pk_name(self.model_cls) == field_name
            is_immutable = (
                is_pk or bool(getattr(orm_model_field, "onupdate", None))
            ) and field_name not in self.readonly_fields
            required = (
                not getattr(orm_model_field, "nullable", False)
                and not getattr(orm_model_field, "default", False)
                and not is_m2m
            )
            choices = (
                orm_model_field.type._object_lookup
                if hasattr(orm_model_field, "type")
                and hasattr(orm_model_field.type, "_object_lookup")
                else {}
            )

            form_widget_type = WidgetType.Input
            form_widget_props: dict[str, Any] = {
                "required": required,
                "disabled": field_name in self.readonly_fields,
                "readOnly": field_name in self.readonly_fields,
            }
            filter_widget_type = WidgetType.Input
            filter_widget_props: dict[str, Any] = {
                "required": False,
            }

            # columns
            match field_type:
                case "String":
                    form_widget_type = WidgetType.Input
                    filter_widget_type = WidgetType.Input
                case "Text":
                    form_widget_type = WidgetType.TextArea
                    filter_widget_type = WidgetType.TextArea
                case "Boolean":
                    form_widget_type = WidgetType.Switch
                    form_widget_props["required"] = False
                    filter_widget_type = WidgetType.RadioGroup
                    filter_widget_props["options"] = [
                        {"label": "Yes", "value": True},
                        {"label": "No", "value": False},
                    ]
                case "ARRAY":
                    form_widget_type = WidgetType.Select
                    form_widget_props["mode"] = "tags"
                    filter_widget_type = WidgetType.Select
                    filter_widget_props["mode"] = "tags"
                case "Integer" | "Float" | "Decimal":
                    form_widget_type = WidgetType.InputNumber
                    filter_widget_type = WidgetType.InputNumber
                case "Date":
                    form_widget_type = WidgetType.DatePicker
                    form_widget_props["format"] = settings.ADMIN_DATE_FORMAT
                    filter_widget_type = WidgetType.RangePicker
                    filter_widget_props["format"] = settings.ADMIN_DATE_FORMAT
                case "DateTime":
                    form_widget_type = WidgetType.DateTimePicker
                    form_widget_props["format"] = settings.ADMIN_DATETIME_FORMAT
                    filter_widget_type = WidgetType.RangePicker
                    filter_widget_props["format"] = settings.ADMIN_DATETIME_FORMAT
                    filter_widget_props["showTime"] = True
                case "Time":
                    form_widget_type = WidgetType.TimePicker
                    form_widget_props["format"] = settings.ADMIN_TIME_FORMAT
                    filter_widget_type = WidgetType.RangePicker
                    filter_widget_props["format"] = settings.ADMIN_TIME_FORMAT
                    filter_widget_props["showTime"] = True
                case "Enum":
                    form_widget_props["options"] = [
                        {"label": k, "value": v} for k, v in choices.items()
                    ]
                    filter_widget_props["options"] = [
                        {"label": k, "value": v} for k, v in choices.items()
                    ]
                    if field_name in self.radio_fields:
                        form_widget_type = WidgetType.RadioGroup
                        filter_widget_type = WidgetType.CheckboxGroup
                    else:
                        form_widget_type = WidgetType.Select
                        filter_widget_type = WidgetType.Select
                        filter_widget_props["mode"] = "multiple"
                case "JSON":
                    form_widget_type = WidgetType.JsonTextArea

            # relations
            if field_type in (
                "ONETOONE",
                "MANYTOONE",
                "MANYTOMANY",
            ):
                rel_model_cls = getattrs(orm_model_field, "entity.class_")
                rel_model = rel_model_cls.__name__
                rel_model_id_field = self.get_model_pk_name(rel_model_cls)
                rel_model_label_fields = ("__str__", rel_model_id_field)

                match field_type:
                    case "ONETOONE":
                        if field_name in self.raw_id_fields:
                            form_widget_type = WidgetType.Input
                            filter_widget_type = WidgetType.Input
                        else:
                            form_widget_type = WidgetType.AsyncSelect
                            form_widget_props["parentModel"] = rel_model
                            form_widget_props["idField"] = rel_model_id_field
                            form_widget_props["labelFields"] = rel_model_label_fields
                            filter_widget_type = WidgetType.AsyncSelect
                            filter_widget_props["mode"] = "multiple"
                            filter_widget_props["parentModel"] = rel_model
                            filter_widget_props["idField"] = rel_model_id_field
                            filter_widget_props["labelFields"] = rel_model_label_fields
                    case "MANYTOONE":
                        if field_name in self.raw_id_fields:
                            form_widget_type = WidgetType.Input
                            filter_widget_type = WidgetType.Input
                        else:
                            form_widget_type = WidgetType.AsyncSelect
                            form_widget_props["parentModel"] = rel_model
                            form_widget_props["idField"] = rel_model_id_field
                            form_widget_props["labelFields"] = rel_model_label_fields
                            filter_widget_type = WidgetType.AsyncSelect
                            filter_widget_props["mode"] = "multiple"
                            filter_widget_props["parentModel"] = rel_model
                            filter_widget_props["idField"] = rel_model_id_field
                            filter_widget_props["labelFields"] = rel_model_label_fields
                    case "MANYTOMANY":
                        if field_name in self.raw_id_fields:
                            form_widget_type = WidgetType.Input
                            filter_widget_type = WidgetType.Input
                        else:
                            form_widget_props["parentModel"] = rel_model
                            form_widget_props["idField"] = rel_model_id_field
                            form_widget_props["labelFields"] = rel_model_label_fields
                            filter_widget_props["parentModel"] = rel_model
                            filter_widget_props["idField"] = rel_model_id_field
                            filter_widget_props["labelFields"] = rel_model_label_fields
                            if (
                                field_name in self.filter_vertical
                                or field_name in self.filter_horizontal
                            ):
                                form_widget_type = WidgetType.AsyncTransfer
                                form_widget_props["layout"] = (
                                    "vertical"
                                    if field_name in self.filter_vertical
                                    else "horizontal"
                                )
                                filter_widget_type = WidgetType.AsyncTransfer
                                filter_widget_props["layout"] = (
                                    "vertical"
                                    if field_name in self.filter_vertical
                                    else "horizontal"
                                )
                            else:
                                form_widget_type = WidgetType.AsyncSelect
                                form_widget_props["mode"] = "multiple"
                                filter_widget_type = WidgetType.AsyncSelect
                                filter_widget_props["mode"] = "multiple"

            form_widget_type, form_widget_props = self.formfield_overrides.get(
                field_name, (form_widget_type, form_widget_props)
            )
            fields.append(
                ModelFieldWidgetSchema(
                    name=field_name,
                    column_name=column_name,
                    is_m2m=is_m2m,
                    is_pk=is_pk,
                    is_immutable=is_immutable,
                    form_widget_type=form_widget_type,
                    form_widget_props=form_widget_props,
                    filter_widget_type=filter_widget_type,
                    filter_widget_props=filter_widget_props,
                )
            )
        for custom_column in self.custom_columns:
            fields.append(
                ModelFieldWidgetSchema(
                    name=custom_column.column_name,
                    column_name=custom_column.column_name,
                    is_m2m=False,
                    is_pk=False,
                    is_immutable=False,
                    form_widget_type=custom_column.widget_type,
                    form_widget_props={"required": False},
                    filter_widget_type=custom_column.widget_type,
                    filter_widget_props={"required": False},
                )
            )
        return fields
