# REST API client for ServiceDesk Plus

## 1) Методы

##### 1.1) `get_request` - получение заявки по id

##### 1.2) `get_requests` - получение заявок по условиям

##### 1.3) `create_request` - создание заявки

##### 1.4) `update_request` - обновление заявки

##### 1.5) `cancel_request` - отмена заявки

##### 1.6) `attach_file_to_request` - прикрепление файлов к заявке

##### 1.7) `get_categories` - получение категорий

##### 1.8) `get_service_categories` - получение категорий услуг

##### 1.9) `get_subcategories` - получение подкатегорий

##### 1.10) `get_templates` - получение шаблонов для заявок

##### 1.11) `get_template` - получение шаблона по id

##### 1.12) `get_urgencies` - получение возможных значений срочности заявок

##### 1.13) `add_note` - добавление заметок к заявке

##### 1.14) `get_resolution` - получение решения заявки

<br />

Все методы могут вызывать исключения `HelpdeskClientError` и `httpx.HTTPError`

## 2) Установка

### pip

```
pip install servicedesk-client
```

### pdm

```
pdm add servicedesk-client
```

## 3) Пример внедрения

### 3.1) Настройки

```python
class HelpdeskSettings(BaseSettings):
    model_config = SettingsConfigDict(str_strip_whitespace=True, env_prefix="helpdesk_")

    authtoken: SecretStr
    base_url: str
    timeout: int
```

### 3.2) Http Client

```python
HelpdeskHttpClient = NewType("HelpdeskHttpClient", httpx.AsyncClient)

@asynccontextmanager
async def get_helpdesk_http_client(
    settings: HelpdeskSettings,
) -> AsyncIterator[HelpdeskHttpClient]:

    async with httpx.AsyncClient(
        headers={"authtoken": settings.authtoken.get_secret_value()},
        base_url=settings.base_url,
        timeout=settings.timeout,
    ) as client:
        yield HelpdeskHttpClient(client)
```

### 3.3) DI (используется библиотека https://pypi.org/project/aioinject/)

```python
from helpdesk_client.v3 import HelpdeskClient


@asynccontextmanager
async def _get_helpdesk_client(
    http_client: HelpdeskHttpClient,
) -> AsyncIterator[HelpdeskClient]:
    yield HelpdeskClient(http_client=http_client)


PROVIDERS: Providers = [
    aioinject.Singleton(get_helpdesk_http_client, HelpdeskHttpClient),
    aioinject.Singleton(_get_helpdesk_client),
]
```

### 3.4) Helpdesk Service

```python
from helpdesk_client.v3 import HelpdeskClient


class HelpdeskService:
    def __init__(self, helpdesk_client: HelpdeskClient) -> None:
        self._helpdesk_client = helpdesk_client

    ...
```

## 4) Пример получения 5 последних заявок

```python
import httpx
from helpdesk_client.enums import SortEnum
from helpdesk_client.exceptions import HelpdeskClientError
from helpdesk_client.v3 import HelpdeskClient
from helpdesk_client.v3.schemas import (
    RequestFilterParams,
    RequestListSchema,
    RequestSearchFields,
)
from result import as_async_result


class HelpdeskService:
    def __init__(self, helpdesk_client: HelpdeskClient) -> None:
        self._helpdesk_client = helpdesk_client

    @as_async_result(HelpdeskClientError, httpx.HTTPError)
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

Не удалось составить запрос для получения списка заявок по почте заявителя. Поэтому для запроса используются `ФИО` или `helpdesk_id`.

`ФИО` в редких случаях могут повторяться у разных людей (возможны коллизии), но `helpdesk_id` доступен не всегда, поэтому является опциональным. В примере `helpdesk_id` используется в запросе только тогда, когда передается в метод.
