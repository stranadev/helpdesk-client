import re

from pydantic import BaseModel


def json_dump_model(value: BaseModel | None) -> str | None:
    if value is None:
        return None

    return value.model_dump_json(exclude_unset=True, by_alias=True)


def remove_html_tags(value: str) -> str:
    return re.sub(r"<[^<]+?>", "", value)
