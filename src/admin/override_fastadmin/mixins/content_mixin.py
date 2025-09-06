import base64
from io import BytesIO
from typing import Any

from src.admin.override_fastadmin.utils import ContentParameter, DocumentPreview, compress_image
from src.unit_of_work import UnitOfWork
from src.utils.repository import SQLAlchemyRepository
from src.utils.log import logger


class ContentMixin:

    # инструкция, которая указывает в каких полях находятся объекты
    content_parameters: list[ContentParameter] = list()

    async def process_incoming_record_with_objects(self, record_id: int, payload: dict[str, Any]) -> None:
        """
        id: int - id записи, к которой прикрепили фото
        payload: dict[str, Any] - словарь, который содержит все поля переданные с фронтенда
        (в том числе payload[название_поля] = [имена фото | base64 новой записи])
        """
        uow = UnitOfWork()
        async with uow:
            for content_parameter in self.content_parameters:
                repo: SQLAlchemyRepository = content_parameter.content_repository(uow.db_session)

                incoming_objects = payload.get(content_parameter.column_name, [])
                existing_objects, new_objects = self._distribute_objects(incoming_objects)
                existing_in_db_objects = await self.get_object_names_existing_in_db(repo, content_parameter, record_id)
                objects_need_to_delete = await self.get_object_names_to_delete(existing_objects, existing_in_db_objects)
                await self.delete_objects_from_record(uow, repo, content_parameter, objects_need_to_delete)
                await self.upload_new_objects(uow, repo, content_parameter, record_id, new_objects)

                await uow.commit()
    
    async def delete_all_objects_of_record(self, record_id: int) -> None:
        """
        получили id основной записи
        перебрали записи, где relation_id_field_name == этому id
        удалил в s3 эти записи
        удалил все - relation_id_field_name == этому id
        """
        uow = UnitOfWork()
        async with uow:
            for content_parameter in self.content_parameters:
                repo: SQLAlchemyRepository = content_parameter.content_repository(
                    uow.db_session
                )
                object_names = await self.get_object_names_existing_in_db(repo, content_parameter, record_id)
                await self.delete_objects_from_record(uow, repo, content_parameter, object_names)
    
    async def get_objects_of_record(self, record_id: int) -> dict[str, list[str]]:
        """
        получили id основной записи
        перебрали записи, где relation_id_field_name == этому id
        собрали имена имагов со всех записей и превратили их в ссылки
        (сортирнуть по create_date)
        """
        uow = UnitOfWork()
        result: dict[str, list[str]] = dict()
        async with uow:
            for content_parameter in self.content_parameters:
                result[content_parameter.column_name] = list()
                repo: SQLAlchemyRepository = content_parameter.content_repository(
                    uow.db_session
                )
                object_names = await self.get_object_names_existing_in_db(repo, content_parameter, record_id)
                for object_name in object_names:
                    if content_parameter.image_type:
                        img_url = await self._create_real_url(uow, object_name)
                    else:
                        img_url = await self._create_preview_url(uow, object_name)
                    result[content_parameter.column_name].append(img_url)
        return result


    async def get_object_names_to_delete(
        self,
        existing_objects: list[str],
        existing_in_db_objects: list[str]
    ):
        # существующие объекты приходят в формате ссылки
        existing_images_names = {
            self._get_filename_from_existing_object(obj)
            for obj in existing_objects
        }
        return list(set(existing_in_db_objects) - set(existing_images_names))

    async def get_object_names_existing_in_db(
        self,
        repo: SQLAlchemyRepository,
        content_parameter: ContentParameter,
        record_id: int,
    ) -> list[str]:
        existing_objects = await repo.find_filtered(
            sort_by="",
            **{content_parameter.relation_id_field_name: record_id},
            **content_parameter.extra_payload_fields,
        )
        existing_object_names_db = [
            getattr(obj, content_parameter.image_field_name)
            for obj in existing_objects
        ]
        return existing_object_names_db

    async def delete_objects_from_record(
        self,
        uow: UnitOfWork,
        repo: SQLAlchemyRepository,
        content_parameter: ContentParameter,
        object_names: list[str]
    ) -> None:
        for object_name in object_names:
            await uow.file_storage.delete_file_by_filename(object_name)
            await repo.delete_filtered(**{content_parameter.image_field_name: object_name})

    async def upload_new_objects(
        self,
        uow: UnitOfWork,
        repo: SQLAlchemyRepository,
        content_parameter: ContentParameter,
        record_id: int,
        new_objects: list[Any]
    ) -> None:

        for new_object in new_objects:
            new_image_name = await self._upload_object(uow, new_object)
            await repo.add_one(
                **{
                    content_parameter.relation_id_field_name: record_id,
                    content_parameter.image_field_name: new_image_name,
                },
                **content_parameter.extra_payload_fields,
            )

                

    async def _upload_object(self, uow: UnitOfWork, object: str) -> str:
        # data:image/jpeg;base64...
        metadata, file_base64 = object.split(";base64,")
        mimetype = metadata.replace("data:", "")
        file = BytesIO(base64.b64decode(file_base64))
        logger.debug("metadata: %s ; mimetype %s", metadata, mimetype)
        if mimetype in ["image/png", "image/jpeg"]:
            logger.debug("Start compressing object")
            old_size_nbytes = file.getbuffer().nbytes
            file = compress_image(file, mimetype.split("/")[-1])
            new_size_nbytes = file.getbuffer().nbytes
            logger.debug("compressing: was %s, became %s, compressing %s", old_size_nbytes, new_size_nbytes, new_size_nbytes/old_size_nbytes)

        return await uow.file_storage.upload_file(file, mimetype)
    
    async def _create_real_url(self, uow: UnitOfWork, object_name: str) -> str:
        return uow.file_storage.get_file_url(object_name)
    
    async def _create_preview_url(self, uow: UnitOfWork, object_name: str) -> str:
        preview_url = await DocumentPreview(uow).get_preview(object_name)
        preview_url += f"?object={object_name}"
        return preview_url

    def _distribute_objects(self, objects: list[str]) -> tuple[list[str], list[str]]:
        existing_objects = []
        new_objects = []

        for object in objects:
            if self._is_object_exist(object):
                existing_objects.append(object)
            else:
                new_objects.append(object)
        return (existing_objects, new_objects)

    def _is_object_exist(self, object: str) -> bool:
        if object.startswith("http"):
            return True
        elif object.startswith("data"):
            return False
        else:
            logger.warning(f"uploading_object is strange {object[:30]}")
            return True

    def _get_filename_from_existing_object(self, object: str) -> str:
        if "?object=" in object:
            return object.split("?object=")[-1]
        return object.split("/")[-1]
