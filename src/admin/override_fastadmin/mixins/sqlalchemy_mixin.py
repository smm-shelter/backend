from typing import Any, Generic, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import BIGINT, Integer

from src.admin.override_fastadmin.utils import CustomColumn
from src.unit_of_work import UnitOfWork
from src.utils.exceptions import ResultNotFound, WrongCredentials
from src.utils.repository import SQLAlchemyRepository, SQLALchemyUserRepository

derived_base_model = TypeVar("derived_base_model", bound=BaseModel)
_sentinel: Any = object()


class SqlAlchemyMixin(Generic[derived_base_model]):
    schemaCreate: Type[derived_base_model]
    schemaUpdate: Type[derived_base_model]
    schemaGet: Type[derived_base_model]
    schemaList: Type[derived_base_model]

    model_repository = _sentinel

    custom_columns: list[CustomColumn]

    async def orm_get_list(
        self,
        options: list[Any],
        joins: list[Any],
        ready_filters: list[Any],
        sort_by: Optional[Any],
        offset: int,
        limit: int,
    ) -> tuple[list[dict[str, Any]], int]:
        uow = UnitOfWork()
        async with uow:
            repo: SQLAlchemyRepository = self.model_repository(uow.db_session)
            count = await repo.count_filtered_by_fastadmin(joins, ready_filters)
            result = await repo.find_filtered_by_fastadmin(
                options,
                joins,
                ready_filters,
                sort_by,
                offset=(offset or 0),
                limit=(limit or 10),
            )
            return (
                [
                    self.schemaList(**obj.__dict__).model_dump(exclude_none=True)
                    | {"__str__": str(obj)}
                    | {
                        custom_column.column_name: custom_column.get_new_value(obj)
                        for custom_column in self.custom_columns
                    }
                    for obj in result
                ],
                count,
            )

    async def orm_get_obj(self, id: int) -> dict[str, Any] | None:
        uow = UnitOfWork()
        async with uow:
            repo: SQLAlchemyRepository = self.model_repository(uow.db_session)
            try:
                obj = await repo.find_one(id=id)
            except ResultNotFound:
                return None

            return self.schemaGet(**obj.__dict__).model_dump(exclude_none=True)

    async def orm_save_obj(self, id: int | None, payload: dict) -> int:
        uow = UnitOfWork()
        if id:
            payload = self.schemaUpdate(**payload).model_dump(exclude_none=True)
        else:
            payload = self.schemaCreate(**payload).model_dump()
        async with uow:
            repo: SQLAlchemyRepository = self.model_repository(uow.db_session)
            if id:
                result = await repo.edit_one(id, **payload)
            else:
                result = await repo.add_one(**payload)
            await uow.commit()
        return result.id

    async def orm_delete_obj(self, id: int) -> None:
        uow = UnitOfWork()
        async with uow:
            repo: SQLAlchemyRepository = self.model_repository(uow.db_session)
            await repo.delete_one(id)
            await uow.commit()

    async def orm_save_upload_field(self, obj: Any, field: str, base64: str) -> None:
        return None

    async def authenticate(self, phone: str, password: str) -> int | None:
        uow = UnitOfWork()
        async with uow:
            repo: SQLALchemyUserRepository = self.model_repository(uow.db_session)
            try:
                user = await repo.authenticate(phone, password)
                return user.id
            except WrongCredentials:
                return None
            except ResultNotFound:
                print(phone, password)
                return None

    async def change_password(self, id: int, password: str) -> None:
        uow = UnitOfWork()
        async with uow:
            repo: SQLALchemyUserRepository = self.model_repository(uow.db_session)
            await repo.change_password(id, password)
            await uow.commit()

    @staticmethod
    def serialize_filters(
        model_cls: Any,
        input_filters: dict[str, Any],
        custom_columns: list[CustomColumn],
    ) -> list[Any]:
        result_filters = list()

        for field_with_condition, value in input_filters.items():
            field = field_with_condition[0]
            condition = field_with_condition[1]

            for custom_column in custom_columns:
                if custom_column.column_name == field:
                    result_filters.append(custom_column.filter[condition](value))
                    break
            else:
                model_field = getattr(model_cls, field)
                if isinstance(model_field.expression.type, BIGINT | Integer):
                    value = int(value)

                match condition:
                    case "lte":
                        result_filters.append(model_field >= value)
                    case "gte":
                        result_filters.append(model_field <= value)
                    case "lt":
                        result_filters.append(model_field > value)
                    case "gt":
                        result_filters.append(model_field < value)
                    case "exact":
                        result_filters.append(model_field == value)
                    case "contains":
                        result_filters.append(model_field.like(f"%{value}%"))
                    case "icontains":
                        result_filters.append(model_field.ilike(f"%{value}%"))
                    case "in":
                        if isinstance(value, list):
                            result_filters.append(model_field in value)
                        else:
                            result_filters.append(model_field == value)
        return result_filters
