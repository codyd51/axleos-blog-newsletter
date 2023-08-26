import datetime
import json
import logging
from dataclasses import asdict
from pathlib import Path

import falcon
from models.subscribed_users import (SubscribedUser,
                                     get_subscribed_users_collection)
from pydantic import BaseModel
from templates import ADMIN_JINJA_ENVIRONMENT, TemplateContext
from utils.email import send_email

from newsletter.utils.api import parse_json_body

_logger = logging.getLogger(__name__)


class SendNewsletterRequest(BaseModel):
    api_key: str
    post_title: str
    post_intro: str
    post_link: str


class SendNewsletterResource:
    def on_get(self, _request: falcon.Request, response: falcon.Response) -> None:
        _logger.info("Serving admin page...")

        now = datetime.datetime.utcnow()
        context = TemplateContext(
            # TODO(PT): Dynamically generate these colors
            generated_at=now.strftime("%B %d, %Y at %H:%M"),
            should_include_unsubscribe_button=False,
            should_include_user_metadata=False,
        )
        response.content_type = falcon.MEDIA_HTML
        response.text = ADMIN_JINJA_ENVIRONMENT.get_template("send_newsletter_admin_ui.html.jinja2").render(
            asdict(context)
        )

    def on_post(self, request: falcon.Request, response: falcon.Response) -> None:
        api_key_path = Path(__file__).parents[2] / "axleos-blog-newsletter-internal-api-key.json"
        api_key = json.loads(api_key_path.read_bytes())["api-key"]

        newsletter_request = parse_json_body(request, SendNewsletterRequest)
        if newsletter_request.api_key != api_key:
            raise falcon.HTTPForbidden(description="Invalid API key")

        _logger.info("Dispatching newsletter...")

        users_collection = get_subscribed_users_collection()

        users_collection.count()
        _logger.info(f"Sending newsletter to {users_collection.count()} emails...")
        for user_snap in users_collection.stream():
            user = SubscribedUser.from_snapshot(user_snap)
            _logger.info(f"Sending newsletter to {user.user_email}...")
            send_email(
                to_user=user,
                subject=f"New Post: {newsletter_request.post_title}",
                template_name="send_newsletter.html.jinja2",
                should_include_unsubscribe_button=True,
                extra_jinja_context={
                    "post_title": newsletter_request.post_title,
                    "post_intro": newsletter_request.post_intro,
                    "post_link": newsletter_request.post_link,
                },
            )

        _logger.info(f"All done dispatching emails")
        response.text = json.dumps({})
