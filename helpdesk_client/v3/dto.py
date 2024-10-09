from dataclasses import dataclass
from io import BufferedReader


@dataclass(frozen=True, slots=True)
class UploadFileDTO:
    file: BufferedReader
    filename: str
    content_type: str
