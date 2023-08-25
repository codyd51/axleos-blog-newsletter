import json
import logging
import datetime
from dataclasses import asdict
from pathlib import Path

import falcon
from pydantic import BaseModel
from sendgrid import Bcc
from sendgrid import Personalization
from sendgrid import To
from sendgrid.helpers.mail import Mail

from clients.sendgrid import get_sendgrid_client
from models.subscribed_users import get_subscribed_users_collection
from newsletter.utils.api import parse_json_body
from templates import ADMIN_JINJA_ENVIRONMENT
from templates import EMAIL_JINJA_ENVIRONMENT
from templates import TemplateContext
from utils.timedelta import format_timedelta

_logger = logging.getLogger(__name__)


class SendNewsletterRequest(BaseModel):
    api_key: str


class SendNewsletterResource:
    def on_get(self, _request: falcon.Request, response: falcon.Response) -> None:
        _logger.info("Serving admin page...")

        now = datetime.datetime.utcnow()
        context = TemplateContext(
            # TODO(PT): Dynamically generate these colors
            background_color="rgb(254, 255, 252)",
            border_color="rgb(197, 198, 195)",
            generated_at=now.strftime("%B %d, %Y at %H:%M"),
            should_include_unsubscribe_button=False,
            should_include_user_metadata=False,
        )
        response.content_type = falcon.MEDIA_HTML
        response.text = ADMIN_JINJA_ENVIRONMENT.get_template("send_newsletter_admin_ui.html.jinja2").render(asdict(context))

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

        message = Mail(
            from_email='backend@axleos.com',
            subject='Test message',
            html_content='Test body'
        )
        personalization = Personalization()
        personalization.add_to(To('backend@axleos.com'))
        for recipient in emails:
            personalization.add_bcc(Bcc(recipient))
        message.add_personalization(personalization)

        sendgrid_client = get_sendgrid_client()
        sendgrid_response = sendgrid_client.send(message)
        _logger.info(f"Dispatched newsletter with Sendgrid, status_code={sendgrid_response.status_code}")

        response.text = json.dumps({})
