from collections.abc import Sequence
from datetime import datetime
from typing import Annotated

import pydantic

from helpdesk_client.types_ import BaseSchema
from helpdesk_client.utils import remove_html_tags

from .pagination import PaginationInfo


class PaginationResponseSchema(PaginationInfo, BaseSchema):
    has_next: bool = pydantic.Field(alias="has_more_rows")
    total_count: int | None = None
    page_: int | None = pydantic.Field(None, alias="page")
    page_number: int | None = None

    @property
    def total_count_(self) -> int:
        if self.total_count is None:
            raise ValueError

        return self.total_count

    @property
    def page(self) -> int:
        if self.page_ is None and self.page_number is None:
            raise ValueError

        return self.page_ or self.page_number # type: ignore[return-value]


class PaginationBaseResponse(BaseSchema):
    list_info: PaginationResponseSchema


class HasNameSchema(BaseSchema):
    name: str


class RequesterSchema(BaseSchema):
    id: int
    email: str | None = pydantic.Field(None, alias="email_id")
    phone: str | None = None
    name: str | None = None


class DateTimeSchema(BaseSchema):
    display_value: str
    """Not in UTC"""

    value: datetime
    """In UTC"""


class RequestSchema(BaseSchema):
    id: int
    subject: str | None = None
    description: str | None = None
    created_time: DateTimeSchema
    due_by_time: DateTimeSchema | None = None
    group: HasNameSchema
    status: HasNameSchema
    requester: RequesterSchema
    technician: RequesterSchema | None = None
    attachments: Sequence["RequestAttachmentSchema"] = pydantic.Field(default_factory=list)
    urgency: "ShortUrgencySchema | None" = None


class RequestListSchema(BaseSchema):
    requests: list[RequestSchema]


class MainRequestSchema(BaseSchema):
    request: RequestSchema


class CategorySchema(BaseSchema):
    id: int
    name: str
    description: str | None = None
    is_deleted: bool = pydantic.Field(alias="deleted")


class ShortCategorySchema(BaseSchema):
    id: int
    name: str


class SubcategorySchema(BaseSchema):
    id: int
    name: str
    description: str | None = None
    is_deleted: bool | None = pydantic.Field(alias="deleted")
    category: ShortCategorySchema


class ShortSubcategorySchema(BaseSchema):
    id: int
    name: str


class ShortUrgencySchema(BaseSchema):
    id: int
    name: str


class UrgencySchema(BaseSchema):
    id: int
    name: str
    description: str | None = None
    is_deleted: bool = pydantic.Field(alias="deleted")


class CategoryPaginationResponseSchema(PaginationBaseResponse):
    categories: Sequence[CategorySchema]

class ServiceCategoryPaginationResponseSchema(PaginationBaseResponse):
    service_categories: Sequence[CategorySchema]


class SubcategoryPaginationResponseSchema(PaginationBaseResponse):
    subcategories: Sequence[SubcategorySchema]


class UrgencyPaginationResponseSchema(PaginationBaseResponse):
    urgencies: Sequence[UrgencySchema]


class FileSizeSchema(BaseSchema):
    display_value: str
    value: int
    """In bytes"""


class RequestAttachmentSchema(BaseSchema):
    id: int
    name: str
    content_url: str
    description: str | None = None
    attached_by: RequesterSchema
    content_type: str | None = None
    attached_on: DateTimeSchema
    size: FileSizeSchema


class MainRequestAttachmentSchema(BaseSchema):
    attachment: RequestAttachmentSchema


class NoteSchema(BaseSchema):
    id: int
    description: str
    added_by: RequesterSchema
    added_time: DateTimeSchema
    show_to_requester: bool


class MainNoteSchema(BaseSchema):
    note: NoteSchema


class ResolutionSchema(BaseSchema):
    content: Annotated[str, pydantic.BeforeValidator(remove_html_tags)]
    submitted_by: RequesterSchema
    submitted_on: DateTimeSchema


class MainResolutionSchema(BaseSchema):
    resolution: ResolutionSchema


class TemplateSchema(BaseSchema):
    id: int
    name: str
    is_service_template: bool
    is_enabled: bool
    inactive: bool
    is_default_template: bool


class TemplatePaginationResponseSchema(PaginationBaseResponse):
    request_templates: Sequence[TemplateSchema]
