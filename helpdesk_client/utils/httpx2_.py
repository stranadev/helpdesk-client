import httpx2

from helpdesk_client.exceptions import HelpdeskClientError


def raise_for_status(response: httpx2.Response) -> None:
    if response.is_success:
        return

    raise HelpdeskClientError(
        status_code=response.status_code,
        response_data=response.content,
    )
