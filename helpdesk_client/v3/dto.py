from dataclasses import dataclass
from typing import IO


@dataclass(frozen=True, slots=True)
class UploadFileDTO:
    file: IO[bytes]
    filename: str
    content_type: str
