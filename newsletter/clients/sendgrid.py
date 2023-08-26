import json
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import ClassVar, Self

from pydantic import BaseModel
from sendgrid import SendGridAPIClient
from utils.credentials_file import CredentialsBackedByFile


class SendGridCredentials(CredentialsBackedByFile):
    _CREDENTIALS_FILE = Path(__file__).parents[2] / "axleos-blog-newsletter-sendgrid-api-keys.json"

    api_key: str


@lru_cache(maxsize=None)
def get_sendgrid_client() -> SendGridAPIClient:
    return SendGridAPIClient(SendGridCredentials.get_default().api_key)
