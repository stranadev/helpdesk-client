from contextlib import suppress
from functools import cached_property
from typing import Any

import orjson
from orjson import JSONDecodeError


class HelpdeskClientError(Exception):
    status_code: int
    response_data: str

    def __init__(self, status_code: int, response_data: bytes) -> None:
        self.status_code = status_code
        self.response_data = response_data.decode()

    def __str__(self) -> str:
        return f"HTTP CODE: {self.status_code}, RESPONSE DATA: {self.response_data}"

    @cached_property
    def json_data(self) -> dict[str, Any] | None:
        if not self.response_data:
            return None

        with suppress(JSONDecodeError):
            return orjson.loads(self.response_data) # type: ignore[no-any-return]

        return None
