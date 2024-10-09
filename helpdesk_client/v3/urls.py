from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HelpdeskUrls:
    v3 = "api/v3"
    requests = f"{v3}/requests"
    request_template = f"{v3}/request_templates"
    categories = f"{v3}/categories"
    service_categories = f"{v3}/service_categories"
    subcategories = f"{v3}/subcategories"
    urgencies = f"{v3}/urgencies"

    @classmethod
    def template_by_id(cls, ident: int) -> str:
        return f"{cls.request_template}/{ident}"

    @classmethod
    def request_by_id(cls, request_id: int) -> str:
        return f"{cls.requests}/{request_id}"

    @classmethod
    def cancel_request(cls, request_id: int) -> str:
        return f"{cls.requests}/{request_id}/cancel"

    @classmethod
    def upload_file(cls, request_id: int) -> str:
        return f"{cls.requests}/{request_id}/upload"

    @classmethod
    def create_note(cls, request_id: int) -> str:
        return f"{cls.requests}/{request_id}/notes"

    @classmethod
    def resolutions(cls, request_id: int) -> str:
        return f"{cls.requests}/{request_id}/resolutions"
