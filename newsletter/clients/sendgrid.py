import json
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import ClassVar
from typing import Self

from pydantic import BaseModel
from sendgrid import SendGridAPIClient


class SendGridCredentials(BaseModel):
    _CREDENTIALS_FILE: ClassVar[Path] = Path(__file__).parents[2] / "axleos-blog-newsletter-sendgrid-api-keys.json"

    api_key: str
    email_validation_api_key: str

    @classmethod
    def get_default(cls) -> Self:
        raw_json = json.loads(cls._CREDENTIALS_FILE.read_bytes())
        return cls.parse_obj(raw_json)


@lru_cache(maxsize=None)
def get_sendgrid_client() -> SendGridAPIClient:
    return SendGridAPIClient(SendGridCredentials.get_default().api_key)


@lru_cache(maxsize=None)
def get_sendgrid_client_for_email_validation() -> SendGridAPIClient:
    return SendGridAPIClient(SendGridCredentials.get_default().email_validation_api_key)


class SendGridEmailValidityEnum(Enum):
    VALID = "Valid"
    RISKY = "Risky"
    INVALID = "Invalid"


class SendGridEmailVerificationResult(BaseModel):
    verdict: SendGridEmailValidityEnum


class SendGridEmailVerificationResponse(BaseModel):
    result: SendGridEmailVerificationResult


def check_email_validity(email: str) -> SendGridEmailValidityEnum:
    client = get_sendgrid_client_for_email_validation()
    raw_response = client.client.validations.email.post(
        request_body={
            "email": email,
            "source": "newsletter_backend",
        }
    )
    print(raw_response)
    print(type(raw_response))
    #raw_response.raise_for_status()
    response = SendGridEmailVerificationResponse.parse_obj(raw_response.body)
    return response.result.verdict


