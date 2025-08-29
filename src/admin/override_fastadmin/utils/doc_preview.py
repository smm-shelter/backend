from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from src.unit_of_work import UnitOfWork

SVG_FILE = """<?xml version="1.0" encoding="utf-8"?>
<svg id="svg2" viewBox="64 64 896 1200" xmlns="http://www.w3.org/2000/svg" focusable="false" data-icon="file" width="1em" height="1em" fill="currentColor" aria-hidden="true">
	<path d="M534 352V136H232v752h560V394H576a42 42 0 01-42-42z" fill="#e6f4ff"></path>
	<path d="M854.6 288.6L639.4 73.4c-6-6-14.1-9.4-22.6-9.4H192c-17.7 0-32 14.3-32 32v832c0 17.7 14.3 32 32 32h640c17.7 0 32-14.3 32-32V311.3c0-8.5-3.4-16.7-9.4-22.7zM602 137.8L790.2 326H602V137.8zM792 888H232V136h302v216a42 42 0 0042 42h216v494z" fill="#1677ff"></path>
	<text style="white-space: pre; fill: rgb(0, 0, 0); font-family: Arial, sans-serif; font-size: 280px;" x="180" y="1250">{text}</text>
</svg>
"""


class DocumentPreview:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_preview(self, filename: str) -> str:
        suffix = Path(filename).suffix[1:]
        preview_name = f"{suffix}.svg"
        if not await self.uow.file_storage.check_object_exists(preview_name):
            svg_object = self._create_svg(suffix)
            await self._publish_svg(svg_object, preview_name)

        return self.uow.file_storage.get_file_url(preview_name)

    async def _publish_svg(self, object: BinaryIO, filename: str) -> None:
        await self.uow.file_storage.upload_file(object, "image/svg+xml", filename)

    def _create_svg(self, text: str) -> BinaryIO:
        svg_file = SVG_FILE.format(text=text)
        return BytesIO(svg_file.encode())
