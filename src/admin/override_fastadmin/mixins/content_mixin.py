import base64
from io import BytesIO
from typing import Any

from src.admin.override_fastadmin.utils import ContentParameter, DocumentPreview
from src.unit_of_work import UnitOfWork
from src.utils.repository import SQLAlchemyRepository


class ContentMixin:
    content_parameters: list[ContentParameter] = list()

    async def upload_objects(self, id: int, payload: dict[str, Any]) -> None:
        """
        получил id основной записи и весь payload (сами отберём нужные поля)
        отделили старые объекты от новых (url vs base64)
        по старым - сверили все ли на месте, если что удалили
        по новым - все добавить
        """
        uow = UnitOfWork()
        for content_parameter in self.content_parameters:
            async with uow:
                repo: SQLAlchemyRepository = content_parameter.content_repository(
                    uow.db_session
                )

                new_images = payload.get(content_parameter.column_name, [])
                existing_images, new_images = self._distribute_objects(new_images)  # type: ignore

                existing_images_names = {
                    self._get_filename_from_existing_object(obj)
                    for obj in existing_images
                }
                existing_objs = await repo.find_filtered(
                    sort_by="",
                    **{content_parameter.relation_id_field_name: id},
                    **content_parameter.extra_payload_fields,
                )
                existing_images_names_db = {
                    getattr(obj, content_parameter.image_field_name)
                    for obj in existing_objs
                }
                images_names_to_delete = (
                    existing_images_names_db - existing_images_names
                )
                for image_name_to_delete in images_names_to_delete:
                    await uow.file_storage.delete_file(image_name_to_delete)
                for existing_obj in existing_objs:
                    image_name = getattr(
                        existing_obj, content_parameter.image_field_name
                    )
                    if image_name in images_names_to_delete:
                        await repo.delete_one(existing_obj.id)

                for new_image in new_images:
                    new_image_name = await self._upload_object(uow, new_image)
                    await repo.add_one(
                        **{
                            content_parameter.relation_id_field_name: id,
                            content_parameter.image_field_name: new_image_name,
                        },
                        **content_parameter.extra_payload_fields,
                    )

                await uow.commit()

    async def _upload_object(self, uow: UnitOfWork, object: str) -> str:
        # data:image/jpeg;base64...
        metadata, file_base64 = object.split(";base64,")
        mimetype = metadata.replace("data:", "")
        file = BytesIO(base64.b64decode(file_base64))
        return await uow.file_storage.upload_file(file, mimetype)

    async def get_objects_of_record(self, id: int) -> dict[str, list[str]]:
        """
        получили id основной записи
        перебрали записи, где relation_id_field_name == этому id
        собрали имена имагов со всех записей и превратили их в ссылки
        (сортирнуть по create_date)
        """
        uow = UnitOfWork()
        result: dict[str, list[str]] = dict()
        for content_parameter in self.content_parameters:
            result[content_parameter.column_name] = list()
            async with uow:
                repo: SQLAlchemyRepository = content_parameter.content_repository(
                    uow.db_session
                )
                objs = await repo.find_filtered(
                    sort_by="id",
                    **{content_parameter.relation_id_field_name: id},
                    **content_parameter.extra_payload_fields,
                )
                for obj in objs:
                    obj_name = getattr(obj, content_parameter.image_field_name)
                    if content_parameter.image_type:
                        img_url = uow.file_storage.get_file_url(obj_name)
                        result[content_parameter.column_name].append(img_url)
                    else:
                        preview_url = await DocumentPreview(uow).get_preview(obj_name)
                        preview_url += f"?object={obj_name}"
                        result[content_parameter.column_name].append(preview_url)

        return result

    async def delete_all_objects_of_record(self, id: int) -> None:
        """
        получили id основной записи
        перебрали записи, где relation_id_field_name == этому id
        удалил в s3 эти записи
        удалил все - relation_id_field_name == этому id
        """
        uow = UnitOfWork()
        for content_parameter in self.content_parameters:
            async with uow:
                repo: SQLAlchemyRepository = content_parameter.content_repository(
                    uow.db_session
                )
                objs = await repo.find_filtered(
                    sort_by="", **{content_parameter.relation_id_field_name: id}
                )
                for obj in objs:
                    img_name = getattr(obj, content_parameter.image_field_name)
                    await uow.file_storage.delete_file(img_name)
                    # TODO: delete from s3
                await repo.delete_filtered(
                    **{content_parameter.relation_id_field_name: id}
                )

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
            print(f"uploading_object is strange {object[:30]}")
            return True

    def _get_filename_from_existing_object(self, object: str) -> str:
        if "?object=" in object:
            return object.split("?object=")[-1]
        return object.split("/")[-1]
