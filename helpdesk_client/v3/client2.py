from contextlib import AbstractAsyncContextManager, AbstractContextManager
from http import HTTPStatus
from typing import Literal

import httpx2

from helpdesk_client.utils._utils import build_files
from helpdesk_client.utils.httpx2_ import raise_for_status
from helpdesk_client.v3.dto import UploadFileDTO
from helpdesk_client.v3.schemas.body import (
    MainNoteCreateSchema,
    MainRequestCreateUpdateSchema,
    NoteCreateSchema,
    RequestCreateSchema,
    RequestUpdateSchema,
    TemplateSchema,
)
from helpdesk_client.v3.schemas.query_params import (
    CategoryFilterParams,
    HelpdeskFilter,
    RequestCriteriaFilterPagePaginationParams,
    RequestFilterPagePaginationParams,
    RequestFilterParams,
    SubcategoryFilterParams,
    TemplateFilterParams,
    UrgencyFilterParams,
)
from helpdesk_client.v3.schemas.response import (
    CategoryPaginationResponseSchema,
    MainNoteSchema,
    MainRequestAttachmentSchema,
    MainRequestWithResolutionSchema,
    MainResolutionSchema,
    NoteSchema,
    RequestAttachmentSchema,
    RequestPaginationResponseSchema,
    RequestSchema,
    RequestWithResolutionSchema,
    ResolutionSchema,
    ServiceCategoryPaginationResponseSchema,
    SubcategoryPaginationResponseSchema,
    TemplatePaginationResponseSchema,
    UrgencyPaginationResponseSchema,
)

from .schemas import MainRequestSchema, RequestListSchema
from .urls import HelpdeskUrls


class HelpdeskClient2:
    def __init__(
        self,
        http_client: httpx2.AsyncClient,
        urls: HelpdeskUrls | None = None,
    ) -> None:
        self._http_client = http_client
        self._urls = urls or HelpdeskUrls()

    async def get_request(self, ident: int) -> RequestSchema | None:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        url = self._urls.request_by_id(ident)
        response = await self._http_client.get(url)
        if response.status_code == HTTPStatus.NOT_FOUND:
            return None

        raise_for_status(response)
        schema = MainRequestSchema.model_validate(response.json())
        return schema.request

    async def get_request_with_resolution(
        self,
        ident: int,
    ) -> RequestWithResolutionSchema | None:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        url = self._urls.request_by_id(ident)
        response = await self._http_client.get(url)
        if response.status_code == HTTPStatus.NOT_FOUND:
            return None

        raise_for_status(response)
        schema = MainRequestWithResolutionSchema.model_validate(response.json())
        return schema.request

    async def get_requests(
        self,
        filter_: RequestFilterParams,
    ) -> RequestListSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        schema = HelpdeskFilter(list_info=filter_)
        params = {
            "input_data": schema.model_dump_json(by_alias=True, exclude_unset=True),
        }
        response = await self._http_client.get(self._urls.requests, params=params)
        raise_for_status(response)
        return RequestListSchema.model_validate(response.json())

    async def get_requests_page_paginated(
        self,
        filter_: (
            RequestFilterPagePaginationParams
            | RequestCriteriaFilterPagePaginationParams
        ),
    ) -> RequestPaginationResponseSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        schema = HelpdeskFilter(list_info=filter_)
        params = {
            "input_data": schema.model_dump_json(by_alias=True, exclude_unset=True),
        }
        response = await self._http_client.get(self._urls.requests, params=params)
        raise_for_status(response)
        return RequestPaginationResponseSchema.model_validate(response.json())

    async def create_request(
        self,
        schema: RequestCreateSchema,
    ) -> RequestSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        main_schema = MainRequestCreateUpdateSchema(request=schema)
        body = {
            "input_data": main_schema.model_dump_json(
                by_alias=True,
                exclude_unset=True,
            ),
        }
        response = await self._http_client.post(self._urls.requests, data=body)
        raise_for_status(response)
        response_schema = MainRequestSchema.model_validate(response.json())
        return response_schema.request

    async def update_request(
        self,
        ident: int,
        schema: RequestUpdateSchema,
    ) -> RequestSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`, `ValueError`"""

        if schema.is_empty:
            msg = "Got schema with empty values"
            raise ValueError(msg)

        url = self._urls.request_by_id(ident)
        main_schema = MainRequestCreateUpdateSchema(request=schema)
        body = {
            "input_data": main_schema.model_dump_json(
                by_alias=True,
                exclude_unset=True,
            ),
        }
        response = await self._http_client.put(url, data=body)
        raise_for_status(response)
        response_schema = MainRequestSchema.model_validate(response.json())
        return response_schema.request

    async def cancel_request(
        self,
        request_id: int,
    ) -> None:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        url = self._urls.cancel_request(request_id)
        response = await self._http_client.put(url)
        raise_for_status(response)

    async def attach_file_to_request(
        self,
        request_id: int,
        dto: UploadFileDTO,
        file_field: Literal["file", "input_file"] = "input_file",
    ) -> RequestAttachmentSchema:
        """
        Прикрепляет файл к заявке.

        :param request_id: Идентификатор заявки
        :param dto: `UploadFileDTO`
        :param file_field: Наименование поля файла. В версии ServiceDesk 14.8 вместо `file` ожидается `input_file`
        raises: `HelpdeskClientError`, `httpx2.HTTPError`
        """

        url = self._urls.upload_file(request_id)
        files = build_files(file_field, dto)
        response = await self._http_client.put(url, files=files)
        raise_for_status(response)
        response_schema = MainRequestAttachmentSchema.model_validate(response.json())
        return response_schema.attachment

    async def get_categories(
        self,
        filter_: CategoryFilterParams,
    ) -> CategoryPaginationResponseSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        schema = HelpdeskFilter(list_info=filter_)
        params = {
            "input_data": schema.model_dump_json(by_alias=True, exclude_unset=True),
        }
        response = await self._http_client.get(self._urls.categories, params=params)
        raise_for_status(response)
        return CategoryPaginationResponseSchema.model_validate(response.json())

    async def get_service_categories(
        self,
        filter_: CategoryFilterParams,
    ) -> ServiceCategoryPaginationResponseSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        schema = HelpdeskFilter(list_info=filter_)
        params = {
            "input_data": schema.model_dump_json(by_alias=True, exclude_unset=True),
        }
        response = await self._http_client.get(
            self._urls.service_categories,
            params=params,
        )
        raise_for_status(response)
        return ServiceCategoryPaginationResponseSchema.model_validate(response.json())

    async def get_subcategories(
        self,
        filter_: SubcategoryFilterParams,
    ) -> SubcategoryPaginationResponseSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        schema = HelpdeskFilter(list_info=filter_)
        params = {
            "input_data": schema.model_dump_json(by_alias=True, exclude_unset=True),
        }
        response = await self._http_client.get(self._urls.subcategories, params=params)
        raise_for_status(response)
        return SubcategoryPaginationResponseSchema.model_validate(response.json())

    async def get_templates(
        self,
        filter_: TemplateFilterParams,
    ) -> TemplatePaginationResponseSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        url = self._urls.request_template
        schema = HelpdeskFilter(list_info=filter_)
        params = {
            "input_data": schema.model_dump_json(by_alias=True, exclude_unset=True),
        }
        response = await self._http_client.get(url, params=params)
        raise_for_status(response)
        return TemplatePaginationResponseSchema.model_validate(response.json())

    async def get_template(
        self,
        ident: int,
    ) -> TemplateSchema | None:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        url = self._urls.template_by_id(ident)
        response = await self._http_client.get(url)
        if response.status_code == HTTPStatus.NOT_FOUND:
            return None

        raise_for_status(response)
        return TemplateSchema.model_validate(response.json())

    async def get_urgencies(
        self,
        filter_: UrgencyFilterParams,
    ) -> UrgencyPaginationResponseSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        schema = HelpdeskFilter(list_info=filter_)
        params = {
            "input_data": schema.model_dump_json(by_alias=True, exclude_unset=True),
        }
        response = await self._http_client.get(self._urls.urgencies, params=params)
        raise_for_status(response)
        return UrgencyPaginationResponseSchema.model_validate(response.json())

    async def add_note(
        self,
        request_id: int,
        schema: NoteCreateSchema,
    ) -> NoteSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        url = self._urls.create_note(request_id)
        main_schema = MainNoteCreateSchema(note=schema)
        body = {
            "input_data": main_schema.model_dump_json(
                by_alias=True,
                exclude_unset=True,
            ),
        }
        response = await self._http_client.post(url, data=body)
        raise_for_status(response)
        return MainNoteSchema.model_validate(response.json()).note

    async def attach_file_to_note(
        self,
        request_id: int,
        note_id: int,
        dto: UploadFileDTO,
        file_field: Literal["file", "input_file"] = "input_file",
    ) -> RequestAttachmentSchema:
        """
        Прикрепляет файл к комментарию/обсуждению.

        :param request_id: Идентификатор заявки
        :param note_id: Идентификатор комментария/обсуждения
        :param dto: `UploadFileDTO`
        :param file_field: Наименование поля файла. В версии ServiceDesk 14.8 вместо `file` ожидается `input_file`
        raises: `HelpdeskClientError`, `httpx2.HTTPError`
        """

        url = self._urls.upload_note_file(request_id=request_id, note_id=note_id)
        files = build_files(file_field, dto)
        response = await self._http_client.put(url, files=files)
        raise_for_status(response)
        response_schema = MainRequestAttachmentSchema.model_validate(response.json())
        return response_schema.attachment

    async def get_resolution(
        self,
        request_id: int,
    ) -> ResolutionSchema | None:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        url = self._urls.resolutions(request_id)
        response = await self._http_client.get(url)
        if response.status_code == HTTPStatus.NOT_FOUND:
            return None

        raise_for_status(response)
        return MainResolutionSchema.model_validate(response.json()).resolution

    async def download(self, content_url: str) -> bytes | None:
        """
        Скачивает ресурс по указанному URL.

        :param content_url: Примеры: 1) `content_url` из `RequestAttachmentSchema`; 2) значение атрибута `src` тега `img` из `ResolutionSchema.raw_content`.
        raises: `HelpdeskClientError`, `httpx2.HTTPError`
        """

        if content_url.startswith("/"):
            content_url = content_url.removeprefix("/")

        response = await self._http_client.get(content_url)
        if response.status_code == HTTPStatus.NOT_FOUND:
            return None

        raise_for_status(response)
        return response.content

    def stream(self, content_url: str) -> AbstractAsyncContextManager[httpx2.Response]:
        """
        Стримит ресурс по указанному URL.

        :param content_url: Примеры: 1) `content_url` из `RequestAttachmentSchema`; 2) значение атрибута `src` тега `img` из `ResolutionSchema.raw_content`.
        raises: `httpx2.HTTPError`
        """

        if content_url.startswith("/"):
            content_url = content_url.removeprefix("/")

        return self._http_client.stream("GET", content_url)


class SyncHelpdeskClient2:
    def __init__(
        self,
        http_client: httpx2.Client,
        urls: HelpdeskUrls | None = None,
    ) -> None:
        self._http_client = http_client
        self._urls = urls or HelpdeskUrls()

    def get_request(self, ident: int) -> RequestSchema | None:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        url = self._urls.request_by_id(ident)
        response = self._http_client.get(url)
        if response.status_code == HTTPStatus.NOT_FOUND:
            return None

        raise_for_status(response)
        schema = MainRequestSchema.model_validate(response.json())
        return schema.request

    def get_request_with_resolution(
        self,
        ident: int,
    ) -> RequestWithResolutionSchema | None:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        url = self._urls.request_by_id(ident)
        response = self._http_client.get(url)
        if response.status_code == HTTPStatus.NOT_FOUND:
            return None

        raise_for_status(response)
        schema = MainRequestWithResolutionSchema.model_validate(response.json())
        return schema.request

    def get_requests(
        self,
        filter_: RequestFilterParams,
    ) -> RequestListSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        schema = HelpdeskFilter(list_info=filter_)
        params = {
            "input_data": schema.model_dump_json(by_alias=True, exclude_unset=True),
        }
        response = self._http_client.get(self._urls.requests, params=params)
        raise_for_status(response)
        return RequestListSchema.model_validate(response.json())

    def get_requests_page_paginated(
        self,
        filter_: (
            RequestFilterPagePaginationParams
            | RequestCriteriaFilterPagePaginationParams
        ),
    ) -> RequestPaginationResponseSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        schema = HelpdeskFilter(list_info=filter_)
        params = {
            "input_data": schema.model_dump_json(by_alias=True, exclude_unset=True),
        }
        response = self._http_client.get(self._urls.requests, params=params)
        raise_for_status(response)
        return RequestPaginationResponseSchema.model_validate(response.json())

    def create_request(
        self,
        schema: RequestCreateSchema,
    ) -> RequestSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        main_schema = MainRequestCreateUpdateSchema(request=schema)
        body = {
            "input_data": main_schema.model_dump_json(
                by_alias=True,
                exclude_unset=True,
            ),
        }
        response = self._http_client.post(self._urls.requests, data=body)
        raise_for_status(response)
        response_schema = MainRequestSchema.model_validate(response.json())
        return response_schema.request

    def update_request(
        self,
        ident: int,
        schema: RequestUpdateSchema,
    ) -> RequestSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`, `ValueError`"""

        if schema.is_empty:
            msg = "Got schema with empty values"
            raise ValueError(msg)

        url = self._urls.request_by_id(ident)
        main_schema = MainRequestCreateUpdateSchema(request=schema)
        body = {
            "input_data": main_schema.model_dump_json(
                by_alias=True,
                exclude_unset=True,
            ),
        }
        response = self._http_client.put(url, data=body)
        raise_for_status(response)
        response_schema = MainRequestSchema.model_validate(response.json())
        return response_schema.request

    def cancel_request(
        self,
        request_id: int,
    ) -> None:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        url = self._urls.cancel_request(request_id)
        response = self._http_client.put(url)
        raise_for_status(response)

    def attach_file_to_request(
        self,
        request_id: int,
        dto: UploadFileDTO,
        file_field: Literal["file", "input_file"] = "input_file",
    ) -> RequestAttachmentSchema:
        """
        Прикрепляет файл к заявке.

        :param request_id: Идентификатор заявки
        :param dto: `UploadFileDTO`
        :param file_field: Наименование поля файла. В версии ServiceDesk 14.8 вместо `file` ожидается `input_file`
        raises: `HelpdeskClientError`, `httpx2.HTTPError`
        """

        url = self._urls.upload_file(request_id)
        files = build_files(file_field, dto)
        response = self._http_client.put(url, files=files)
        raise_for_status(response)
        response_schema = MainRequestAttachmentSchema.model_validate(response.json())
        return response_schema.attachment

    def get_categories(
        self,
        filter_: CategoryFilterParams,
    ) -> CategoryPaginationResponseSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        schema = HelpdeskFilter(list_info=filter_)
        params = {
            "input_data": schema.model_dump_json(by_alias=True, exclude_unset=True),
        }
        response = self._http_client.get(self._urls.categories, params=params)
        raise_for_status(response)
        return CategoryPaginationResponseSchema.model_validate(response.json())

    def get_service_categories(
        self,
        filter_: CategoryFilterParams,
    ) -> ServiceCategoryPaginationResponseSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        schema = HelpdeskFilter(list_info=filter_)
        params = {
            "input_data": schema.model_dump_json(by_alias=True, exclude_unset=True),
        }
        response = self._http_client.get(
            self._urls.service_categories,
            params=params,
        )
        raise_for_status(response)
        return ServiceCategoryPaginationResponseSchema.model_validate(response.json())

    def get_subcategories(
        self,
        filter_: SubcategoryFilterParams,
    ) -> SubcategoryPaginationResponseSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        schema = HelpdeskFilter(list_info=filter_)
        params = {
            "input_data": schema.model_dump_json(by_alias=True, exclude_unset=True),
        }
        response = self._http_client.get(self._urls.subcategories, params=params)
        raise_for_status(response)
        return SubcategoryPaginationResponseSchema.model_validate(response.json())

    def get_templates(
        self,
        filter_: TemplateFilterParams,
    ) -> TemplatePaginationResponseSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        url = self._urls.request_template
        schema = HelpdeskFilter(list_info=filter_)
        params = {
            "input_data": schema.model_dump_json(by_alias=True, exclude_unset=True),
        }
        response = self._http_client.get(url, params=params)
        raise_for_status(response)
        return TemplatePaginationResponseSchema.model_validate(response.json())

    def get_template(
        self,
        ident: int,
    ) -> TemplateSchema | None:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        url = self._urls.template_by_id(ident)
        response = self._http_client.get(url)
        if response.status_code == HTTPStatus.NOT_FOUND:
            return None

        raise_for_status(response)
        return TemplateSchema.model_validate(response.json())

    def get_urgencies(
        self,
        filter_: UrgencyFilterParams,
    ) -> UrgencyPaginationResponseSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        schema = HelpdeskFilter(list_info=filter_)
        params = {
            "input_data": schema.model_dump_json(by_alias=True, exclude_unset=True),
        }
        response = self._http_client.get(self._urls.urgencies, params=params)
        raise_for_status(response)
        return UrgencyPaginationResponseSchema.model_validate(response.json())

    def add_note(
        self,
        request_id: int,
        schema: NoteCreateSchema,
    ) -> NoteSchema:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        url = self._urls.create_note(request_id)
        main_schema = MainNoteCreateSchema(note=schema)
        body = {
            "input_data": main_schema.model_dump_json(
                by_alias=True,
                exclude_unset=True,
            ),
        }
        response = self._http_client.post(url, data=body)
        raise_for_status(response)
        return MainNoteSchema.model_validate(response.json()).note

    def attach_file_to_note(
        self,
        request_id: int,
        note_id: int,
        dto: UploadFileDTO,
        file_field: Literal["file", "input_file"] = "input_file",
    ) -> RequestAttachmentSchema:
        """
        Прикрепляет файл к комментарию/обсуждению.

        :param request_id: Идентификатор заявки
        :param note_id: Идентификатор комментария/обсуждения
        :param dto: `UploadFileDTO`
        :param file_field: Наименование поля файла. В версии ServiceDesk 14.8 вместо `file` ожидается `input_file`
        raises: `HelpdeskClientError`, `httpx2.HTTPError`
        """

        url = self._urls.upload_note_file(request_id=request_id, note_id=note_id)
        files = build_files(file_field, dto)
        response = self._http_client.put(url, files=files)
        raise_for_status(response)
        response_schema = MainRequestAttachmentSchema.model_validate(response.json())
        return response_schema.attachment

    def get_resolution(
        self,
        request_id: int,
    ) -> ResolutionSchema | None:
        """raises: `HelpdeskClientError`, `httpx2.HTTPError`"""

        url = self._urls.resolutions(request_id)
        response = self._http_client.get(url)
        if response.status_code == HTTPStatus.NOT_FOUND:
            return None

        raise_for_status(response)
        return MainResolutionSchema.model_validate(response.json()).resolution

    def download(self, content_url: str) -> bytes | None:
        """
        Скачивает ресурс по указанному URL.

        :param content_url: Примеры: 1) `content_url` из `RequestAttachmentSchema`; 2) значение атрибута `src` тега `img` из `ResolutionSchema.raw_content`.
        raises: `HelpdeskClientError`, `httpx2.HTTPError`
        """

        if content_url.startswith("/"):
            content_url = content_url.removeprefix("/")

        response = self._http_client.get(content_url)
        if response.status_code == HTTPStatus.NOT_FOUND:
            return None

        raise_for_status(response)
        return response.content

    def stream(self, content_url: str) -> AbstractContextManager[httpx2.Response]:
        """
        Стримит ресурс по указанному URL.

        :param content_url: Примеры: 1) `content_url` из `RequestAttachmentSchema`; 2) значение атрибута `src` тега `img` из `ResolutionSchema.raw_content`.
        raises: `httpx2.HTTPError`
        """

        if content_url.startswith("/"):
            content_url = content_url.removeprefix("/")

        return self._http_client.stream("GET", content_url)
