import json
from functools import lru_cache
from pathlib import Path

from sendgrid import SendGridAPIClient


@lru_cache(maxsize=None)
def get_sendgrid_client() -> SendGridAPIClient:
    sendgrid_api_key_path = Path(__file__).parents[2] / "axleos-blog-newsletter-sendgrid-api-key.json"
    sendgrid_api_key = json.loads(sendgrid_api_key_path.read_bytes())["sendgrid-key"]
    return SendGridAPIClient(sendgrid_api_key)
