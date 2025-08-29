from typing import Any, Optional

from sqlalchemy import TextClause, or_, text
from sqlalchemy.orm import selectinload

from .mixins import ContentMixin, FastAdminMixin, SqlAlchemyMixin
from .utils import CustomColumn


class CustomModelAdmin(SqlAlchemyMixin, ContentMixin, FastAdminMixin):
    custom_columns: list[CustomColumn] = list()

    async def get_list(
        self,
        offset: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict | None = None,
    ) -> tuple[list[dict], int]:
        serialized_filters = []
        joins = list(
            {custom_column.join_field for custom_column in self.custom_columns} - {None}
        )
        options = [selectinload(join_field) for join_field in joins]  # type: ignore

        if filters:
            serialized_filters = self.serialize_filters(
                self.model_cls, filters, self.custom_columns
            )

        if search and self.search_fields:
            serialized_filters.append(
                or_(
                    *[
                        getattr(self.model_cls, field).ilike(f"%{search}%")
                        for field in self.search_fields
                    ]
                )
            )
        sort_expression: Optional[TextClause] = None
        if sort_by:
            sort_field = sort_by[1:] if sort_by.startswith("-") else sort_by
            for custom_column in self.custom_columns:
                if custom_column.column_name == sort_field:
                    if custom_column.sort_field is None:
                        sort_expression = None
                    elif sort_by.startswith("-"):
                        sort_expression = custom_column.sort_field.desc()  # type: ignore
                    else:
                        sort_expression = custom_column.sort_field
                    break
            else:
                if sort_by.startswith("-"):
                    sort_expression = text(sort_by[1:] + " desc")
                else:
                    sort_expression = text(sort_by)

        objs_from_orm, count_from_orm = await self.orm_get_list(
            options,
            joins,
            serialized_filters,
            sort_expression,
            offset=(offset or 0),
            limit=(limit or 10),
        )

        return objs_from_orm, count_from_orm

    async def get_obj(self, id: int) -> dict | None:
        result_from_orm = await self.orm_get_obj(id)
        if result_from_orm is None:
            return None

        # rename columns of foreign objects
        for column in self.raw_id_fields:
            if result_from_orm.get(column):
                result_from_orm[column.replace("_id", "")] = result_from_orm[column]
                result_from_orm.pop(column)

        """
        получили словарь с именами в нужных местах от get_objects_of_record()
        слили с результатом
        """
        result_from_content = await self.get_objects_of_record(id)
        result = result_from_orm | result_from_content

        return result

    async def delete_model(self, id: int) -> None:
        """
        перебрали параметры изображений и
        запросили delete_all_objects_of_record()
        отдыхаем
        """
        await self.delete_all_objects_of_record(id)

        await self.orm_delete_obj(id)

    async def save_obj(self, id: int | None, payload: dict) -> int:
        return await self.orm_save_obj(id, payload)

    async def save_model(self, id: int | None, payload: dict) -> dict | None:
        # rename columns of foreign objects
        for column in self.raw_id_fields:
            column_relation = column.replace("_id", "", 1)
            if payload.get(column_relation):
                payload[column] = payload[column_relation]
                payload.pop(column_relation)

        record_id = await self.save_obj(id, payload)

        """
        просто отдаём id и весь payload на upload_objects
        """
        await self.upload_objects(record_id, payload)

        return await self.get_obj(record_id)


admin_models: dict[Any, CustomModelAdmin] = {}
