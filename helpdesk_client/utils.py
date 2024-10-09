import re

import httpx
from pydantic import BaseModel

from .exceptions import HelpdeskClientError


def raise_for_status(response: httpx.Response) -> None:
    if response.is_success:
        return

    raise HelpdeskClientError(
        status_code=response.status_code,
        response_data=response.content,
    )


def json_dump_model(value: BaseModel | None) -> str | None:
    if value is None:
        return None

    return value.model_dump_json(exclude_unset=True, by_alias=True)


def remove_html_tags(value: str) -> str:
    return re.sub(r"<[^<]+?>", "", value)
