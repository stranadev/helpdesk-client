# REST API client for ServiceDesk Plus

## 1) Установка

### pip
```
pip install servicedesk-client
```
### pdm
```
pdm add servicedesk-client
```
### uv
```
uv add servicedesk-client
```

## 2) Особенности
`HelpdeskClient` и `SyncHelpdeskClient` основаны на более не поддерживаемой библиотеке `httpx`.
<br />
Используйте `HelpdeskClient2` и `SyncHelpdeskClient2`, которые основаны на `httpx2` (форк httpx).

## 3) Методы

##### 3.1) `get_request` - получение заявки по id
##### 3.2) `get_request_with_resolution` - получение заявки по id с решением
##### 3.3) `get_requests` - получение заявок с фильтрацией и index пагинацией
##### 3.4) `get_requests_page_paginated` - получение заявок с фильтрацией и page пагинацией
##### 3.5) `create_request` - создание заявки
##### 3.6) `update_request` - обновление заявки
##### 3.7) `cancel_request` - отмена заявки
##### 3.8) `attach_file_to_request` - прикрепление файлов к заявке
##### 3.9) `get_categories` - получение категорий
##### 3.10) `get_service_categories` - получение категорий услуг
##### 3.11) `get_subcategories` - получение подкатегорий
##### 3.12) `get_templates` - получение шаблонов для заявок
##### 3.13) `get_template` - получение шаблона по id
##### 3.14) `get_urgencies` - получение возможных значений срочности заявок
##### 3.15) `add_note` - добавление заметок к заявке
##### 3.16) `attach_file_to_note` - прикрепление файлов к заметке
##### 3.17) `get_resolution` - получение решения заявки
##### 3.18) `download` - скачивает ресурс по указанному URL
##### 3.19) `stream` - стримит ресурс по указанному URL
<br />

Все методы могут вызывать исключения `HelpdeskClientError` и `httpx.HTTPError`/`httpx2.HTTPError` (`stream` только `HTTPError`)

## 4) Пример внедрения

### 4.1) Pydantic Settings 

```python
import functools
from typing import TypeVar

import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

TSettings = TypeVar("TSettings", bound=BaseSettings)


def get_settings(cls: type[TSettings]) -> TSettings:
    dotenv.load_dotenv()
    return cls()


get_settings = functools.lru_cache(get_settings)


class HelpdeskSettings(BaseSettings):
    model_config = SettingsConfigDict(str_strip_whitespace=True, env_prefix="helpdesk_")

    authtoken: SecretStr
    base_url: str
    timeout: int
```

### 4.2) Client

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import NewType

import httpx
from helpdesk_client.v3 import HelpdeskClient2

HelpdeskHttpClient2 = NewType("HelpdeskHttpClient2", httpx2.AsyncClient)


@asynccontextmanager
async def get_helpdesk_http_client(
    settings: HelpdeskSettings,
) -> AsyncGenerator[HelpdeskHttpClient2]:
    async with httpx2.AsyncClient(
        headers={"authtoken": settings.authtoken.get_secret_value()},
        base_url=settings.base_url,
        timeout=settings.timeout,
    ) as client:
        yield HelpdeskHttpClient2(client)


@asynccontextmanager
async def get_helpdesk_client(
    http_client: HelpdeskHttpClient2,
) -> AsyncGenerator[HelpdeskClient2]:
    yield HelpdeskClient2(http_client=http_client)
```

### 4.3) Service

```python
from helpdesk_client.v3 import HelpdeskClient2


class HelpdeskService:
    def __init__(self, helpdesk_client: HelpdeskClient2) -> None:
        self._helpdesk_client = helpdesk_client

    # далее реализовать методы сервиса, из которых вызывать методы клиента
```

### 4.4) DI (используется библиотека https://pypi.org/project/aioinject/)

```python
from collections.abc import Iterable
from typing import Any, TypeAlias

import aioinject

Providers: TypeAlias = Iterable[aioinject.Provider[Any]]

PROVIDERS: Providers = [
    aioinject.Object(get_settings(HelpdeskSettings)),
    aioinject.Singleton(get_helpdesk_http_client, HelpdeskHttpClient2),
    aioinject.Singleton(get_helpdesk_client),
    aioinject.Scoped(HelpdeskService),
]

# далее создать DI-контейнер и зарегистрировать в нем PROVIDERS
```

## 5) Пример получения 5 последних заявок (через `SearchFields`)

```python
import httpx2
from helpdesk_client.enums import SortEnum
from helpdesk_client.exceptions import HelpdeskClientError
from helpdesk_client.v3 import HelpdeskClient2
from helpdesk_client.v3.schemas import (
    RequestFilterParams,
    RequestListSchema,
    RequestSearchFields,
)
from result import as_async_result


class HelpdeskService:
    def __init__(self, helpdesk_client: HelpdeskClient2) -> None:
        self._helpdesk_client = helpdesk_client

    @as_async_result(HelpdeskClientError, httpx2.HTTPError)
    async def get_requests(
        self,
        full_name: str,
        requester_id: int | None,
    ) -> RequestListSchema:
        search_fields = RequestSearchFields(requester_id=requester_id)
        if requester_id is None:
            search_fields = RequestSearchFields(requester_name=full_name)

        return await self._helpdesk_client.get_requests(
            filter_=RequestFilterParams(
                limit=5,
                offset=0,
                sort_field="created_time",
                sort_order=SortEnum.desc,
                search_fields=search_fields,
            ),
        )
```

Этот способ не позволяет получить заявки конкретного пользователя через email (только через id или ФИО).
<br />
Если важен поиск именно по email, используйте `SearchCriteria`.

## 6) Пример получения заявок с пагинацией (через `SearchCriteria`)

```python
from dataclasses import dataclass
from typing import Annotated, cast

import httpx2
from helpdesk_client.enums import (
    SearchCriteriaConditionEnum,
    SearchCriteriaFieldEnum,
    SearchCriteriaLogicalOperatorEnum,
    SortEnum,
)
from helpdesk_client.exceptions import HelpdeskClientError
from helpdesk_client.v3 import HelpdeskClient2
from helpdesk_client.v3.schemas import (
    RequestCriteriaFilterPagePaginationParams,
    RequestFilterPagePaginationParams,
    RequestPaginationResponseSchema,
    SearchCriteria,
)
from pydantic import Field
from result import Err, Ok, Result, as_async_result


@dataclass(frozen=True, slots=True)
class HelpdeskRequestsSortingDTO:
    field: str
    order: SortEnum


class HelpdeskRequestsPaginationDTO(BaseDTO):
    page: Annotated[int, Field(ge=1)] = 1
    page_size: Annotated[int, Field(ge=1, le=100)] = 5
    """row_count"""
    can_include_count: bool = False
    """get_total_count"""


class HelpdeskRequestsBaseFilterDTO(BaseDTO):
    sorting: HelpdeskRequestsSortingDTO | None = None
    pagination: HelpdeskRequestsPaginationDTO = HelpdeskRequestsPaginationDTO()


class HelpdeskRequestsSearchCriteriaFilterDTO(HelpdeskRequestsBaseFilterDTO):
    email: str
    exclude_inactive_requests: bool = False


class HelpdeskService:
    def __init__(self, helpdesk_client: HelpdeskClient2) -> None:
        self._helpdesk_client = helpdesk_client

    async def get_requests_by_search_criteria(
        self,
        dto: HelpdeskRequestsSearchCriteriaFilterDTO,
    ) -> Result[
        RequestPaginationResponseSchema, HelpdeskClientError | httpx2.HTTPError
    ]:
        filter_params = RequestCriteriaFilterPagePaginationParams(
            page=dto.pagination.page,
            page_size=dto.pagination.page_size,
            can_include_count=dto.pagination.can_include_count,
            sort_field=dto.sorting.field if dto.sorting else None,
            sort_order=dto.sorting.order if dto.sorting else None,
            search_criteria=self._build_search_criteria(dto=dto),
        )

        result = await self.get_requests_page_paginated(
            filter_params=filter_params,
        )
        if isinstance(result, Err):
            error_value = cast(
                "HelpdeskClientError | httpx2.HTTPError",
                result.err_value,
            )
            # залогировать error_value
            return Err(error_value)

        return Ok(result.ok_value)

    @as_async_result(HelpdeskClientError, httpx2.HTTPError)
    async def get_requests_page_paginated(
        self,
        filter_params: (
            RequestFilterPagePaginationParams
            | RequestCriteriaFilterPagePaginationParams
        ),
    ) -> RequestPaginationResponseSchema:
        return await self._helpdesk_client.get_requests_page_paginated(
            filter_=filter_params,
        )

    @staticmethod
    def _build_search_criteria(
        dto: HelpdeskRequestsSearchCriteriaFilterDTO,
    ) -> list[SearchCriteria]:
        search_criteria = [
            SearchCriteria(
                field=SearchCriteriaFieldEnum.requester_email,
                value=dto.email,
                condition=SearchCriteriaConditionEnum.eq,
            ),
        ]
        if dto.exclude_inactive_requests:
            search_criteria.extend(
                SearchCriteria(
                    field=SearchCriteriaFieldEnum.status_name,
                    value=value,
                    condition=SearchCriteriaConditionEnum.neq,
                    logical_operator=SearchCriteriaLogicalOperatorEnum.and_,
                )
                for value in ("Completed", "Cancelled")
            )

        return search_criteria
```
