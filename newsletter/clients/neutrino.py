from enum import Enum
from functools import lru_cache
from pathlib import Path

import requests
from pydantic import BaseModel

from utils.credentials_file import CredentialsBackedByFile


class NeutrinoCredentials(CredentialsBackedByFile):
    _CREDENTIALS_FILE = Path(__file__).parents[2] / "axleos-blog-newsletter-neutrino-api-key.json"
    user_id: str
    api_key: str


class NeutrinoEmailValidityEnum(Enum):
    VALID = "Valid"
    INVALID = "Invalid"


class NeutrinoEmailValidationResponse(BaseModel):
    # PT: More fields are present in the API response
    valid: bool


class NeutrinoApiClient:
    def __init__(self, credentials: NeutrinoCredentials) -> None:
        self.credentials = credentials

    def check_email_validity(self, email: str) -> NeutrinoEmailValidityEnum:
        raw_response = requests.get(
            "https://neutrinoapi.net/email-validate",
            params={"email": email},
            headers={
                "User-ID": self.credentials.user_id,
                "API-Key": self.credentials.api_key,
            },
        )
        raw_response.raise_for_status()
        parsed_response = NeutrinoEmailValidationResponse.parse_obj(raw_response.json())
        mapped_validity = {
            True: NeutrinoEmailValidityEnum.VALID,
            False: NeutrinoEmailValidityEnum.INVALID,
        }[parsed_response.valid]
        return mapped_validity


@lru_cache(maxsize=None)
def get_neutrino_client() -> NeutrinoApiClient:
    return NeutrinoApiClient(NeutrinoCredentials.get_default())
