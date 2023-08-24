import json
import logging
from pathlib import Path

import falcon
from pydantic import BaseModel

from models.subscribed_users import get_subscribed_users_collection
from newsletter.utils.api import parse_json_body


_logger = logging.getLogger(__name__)


class SendNewsletterRequest(BaseModel):
    api_key: str


class SendNewsletterResource:
    def on_post(self, request: falcon.Request, response: falcon.Response) -> None:
        api_key_path = Path(__file__).parents[2] / "axleos-blog-newsletter-internal-api-key.json"
        api_key = json.loads(api_key_path.read_bytes())["api-key"]

        newsletter_request = parse_json_body(request, SendNewsletterRequest)
        if newsletter_request.api_key != api_key:
            raise falcon.HTTPForbidden(description="Invalid API key")

        _logger.info("Dispatching newsletter...")

        users_collection = get_subscribed_users_collection()
        emails = [user.get("user_email") for user in users_collection.stream()]
        _logger.info(f"Sending newsletter to {len(emails)} emails...")
        _logger.info(f"Emails: {emails}")

        response.text = json.dumps({})
