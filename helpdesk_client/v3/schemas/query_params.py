from typing import Annotated

import pydantic
from pydantic import PlainSerializer

from helpdesk_client.enums import SortEnum
from helpdesk_client.types_ import BaseSchema
from helpdesk_client.utils import json_dump_model

from .pagination import PaginationInfo


class OrderingParams(BaseSchema):
    sort_field: str | None = None
    sort_order: SortEnum | None = None


class RequestSearchFields(BaseSchema):
    requester_name: str | None = pydantic.Field(None, alias="requester.name")
    requester_id: int | None = pydantic.Field(None, alias="requester.id")


class CategorySearchFields(BaseSchema):
    is_deleted: bool | None = pydantic.Field(None, alias="deleted")
    name: str | None = None


class SubcategorySearchFields(BaseSchema):
    is_deleted: bool | None = pydantic.Field(None, alias="deleted")
    name: str | None = None
    category_name: str | None = pydantic.Field(None, alias="category.name")


class UrgencySearchFields(BaseSchema):
    is_deleted: bool | None = pydantic.Field(None, alias="deleted")
    name: str | None = None


class TemplateSearchFields(BaseSchema):
    is_service_template: bool | None = None
    name: str | None = None
    service_category_id: int | None = pydantic.Field(None, alias="service_category")


JsonDumpedRequestSearchFields = Annotated[
    RequestSearchFields | None,
    PlainSerializer(lambda model: json_dump_model(model), when_used="json"),
]


class RequestFilterParams(PaginationInfo, OrderingParams, BaseSchema):
    search_fields: JsonDumpedRequestSearchFields = None


class CategoryFilterParams(PaginationInfo, OrderingParams, BaseSchema):
    search_fields: Annotated[
        CategorySearchFields | None,
        PlainSerializer(lambda model: json_dump_model(model), when_used="json"),
    ] = None


class SubcategoryFilterParams(PaginationInfo, OrderingParams, BaseSchema):
    search_fields: Annotated[
        SubcategorySearchFields | None,
        PlainSerializer(lambda model: json_dump_model(model), when_used="json"),
    ] = None


class UrgencyFilterParams(PaginationInfo, OrderingParams, BaseSchema):
    search_fields: Annotated[
        UrgencySearchFields | None,
        PlainSerializer(lambda model: json_dump_model(model), when_used="json"),
    ] = None


class TemplateFilterParams(PaginationInfo, OrderingParams, BaseSchema):
    search_fields: Annotated[
        TemplateSearchFields | None,
        PlainSerializer(lambda model: json_dump_model(model), when_used="json"),
    ] = None


class HelpdeskFilter(BaseSchema):
    list_info: (
        RequestFilterParams
        | CategoryFilterParams
        | SubcategoryFilterParams
        | UrgencyFilterParams
        | TemplateFilterParams
    )
