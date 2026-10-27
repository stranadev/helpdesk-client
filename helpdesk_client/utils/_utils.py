import re
from typing import IO, Literal

from pydantic import BaseModel

from helpdesk_client.v3.dto import UploadFileDTO


def json_dump_model(value: BaseModel | None) -> str | None:
    if value is None:
        return None

    return value.model_dump_json(exclude_unset=True, by_alias=True)


def remove_html_tags(value: str) -> str:
    return re.sub(r"<[^<]+?>", "", value)


def build_files(
    field_name: Literal["file", "input_file"],
    dto: UploadFileDTO,
) -> dict[str, tuple[str, IO[bytes], str]]:
    return {field_name: (dto.filename, dto.file, dto.content_type)}
