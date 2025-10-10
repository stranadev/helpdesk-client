from collections.abc import Sequence
from typing import Annotated

import pydantic
from pydantic import PlainSerializer

from helpdesk_client.enums import (
    SearchCriteriaConditionEnum,
    SearchCriteriaFieldEnum,
    SearchCriteriaLogicalOperatorEnum,
    SortEnum,
)
from helpdesk_client.types_ import BaseSchema
from helpdesk_client.utils import json_dump_model

from .pagination import PagePaginationInfo, PaginationInfo


class OrderingParams(BaseSchema):
    sort_field: str | None = None
    sort_order: SortEnum | None = None


class SearchCriteria(BaseSchema):
    field: SearchCriteriaFieldEnum | str
    value: str
    condition: SearchCriteriaConditionEnum | str
    logical_operator: SearchCriteriaLogicalOperatorEnum | str | None = None


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


class RequestFilterPagePaginationParams(PagePaginationInfo, OrderingParams, BaseSchema):
    search_fields: JsonDumpedRequestSearchFields = None


class RequestCriteriaFilterPagePaginationParams(
    PagePaginationInfo,
    OrderingParams,
    BaseSchema,
):
    """
    `search_criteria` JSON example:

    ...
    "search_criteria": [
        {
            "field": "requester.email_id",
            "value": "test@gmail.com",
            "condition": "eq"
        },
        {
            "field": "status.name",
            "value": "Completed",
            "condition": "neq",
            "logical_operator": "and"
        },
        {
            "field": "status.name",
            "value": "Cancelled",
            "condition": "neq",
            "logical_operator": "and"
        }
    ]
    ...
    """

    search_criteria: Sequence[SearchCriteria] | None = None


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
        | RequestFilterPagePaginationParams
        | RequestCriteriaFilterPagePaginationParams
        | CategoryFilterParams
        | SubcategoryFilterParams
        | UrgencyFilterParams
        | TemplateFilterParams
    )
