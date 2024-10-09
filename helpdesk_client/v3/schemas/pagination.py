import pydantic

from helpdesk_client.types_ import BaseSchema


class PaginationInfo(BaseSchema):
    limit: int = pydantic.Field(alias="row_count")
    offset: int = pydantic.Field(alias="start_index")
    can_include_count: bool = pydantic.Field(default=False, alias="get_total_count")
