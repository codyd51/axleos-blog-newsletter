import json
from abc import ABC
from pathlib import Path
from typing import ClassVar, Self

from pydantic import BaseModel


class CredentialsBackedByFile(ABC, BaseModel):
    # Must be set by subclasses
    _CREDENTIALS_FILE: ClassVar[Path]

    @classmethod
    def get_default(cls) -> Self:
        raw_json = json.loads(cls._CREDENTIALS_FILE.read_bytes())
        return cls.parse_obj(raw_json)
