from typing import Any

import pydantic

from helpdesk_client.types_ import BaseSchema


class IdentSchema(BaseSchema):
    id: int


class TemplateSchema(BaseSchema):
    id: int
    is_service_template: bool | None = None
    service_category: IdentSchema | None = None
    """Subcategory"""


class ShortRequesterSchema(BaseSchema):
    id: int | None = None
    name: str | None = None
    email: str | None = pydantic.Field(None, alias="email_id")
    phone: str | None = None


class RequestCreateSchema(BaseSchema):
    subject: str
    description: str
    requester: ShortRequesterSchema
    template: TemplateSchema | None = None
    urgency: IdentSchema
    mode: IdentSchema | None = None
    udf_fields: dict[str, Any] | None = None


class RequestUpdateSchema(BaseSchema):
    subject: str | None = None
    description: str | None = None
    urgency: IdentSchema | None = None

    @property
    def is_empty(self) -> bool:
        return all(value is None for _, value in self)


class MainRequestCreateUpdateSchema(BaseSchema):
    request: RequestCreateSchema | RequestUpdateSchema


class NoteCreateSchema(BaseSchema):
    description: str
    show_to_requester: bool
    mark_first_response: bool
    add_to_linked_requests: bool


class MainNoteCreateSchema(BaseSchema):
    note: NoteCreateSchema
