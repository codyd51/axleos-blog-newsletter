import datetime
import logging
from dataclasses import asdict
from typing import Any

from clients.sendgrid import get_sendgrid_client
from models.subscribed_users import SubscribedUser
from sendgrid import From, Mail, Personalization, To
from templates import EMAIL_JINJA_ENVIRONMENT, TemplateContext
from utils.timedelta import format_timedelta

_logger = logging.getLogger(__name__)


def send_email(
    to_user: SubscribedUser,
    subject: str,
    template_name: str,
    should_include_unsubscribe_button: bool = True,
    extra_jinja_context: dict[str, Any] | None = None,
):
    _logger.info(f"Sending a {template_name} email to {to_user.user_email}...")
    now = datetime.datetime.utcnow()
    subscription_duration = now.replace(tzinfo=None) - to_user.date_created.replace(tzinfo=None)

    context = TemplateContext(
        # TODO(PT): Dynamically generate these colors
        background_color="rgb(254, 255, 252)",
        border_color="rgb(197, 198, 195)",
        generated_at=now.strftime("%B %d, %Y at %H:%M"),
        should_include_unsubscribe_button=should_include_unsubscribe_button,
        should_include_user_metadata=True,
        user_email=to_user.user_email,
        subscription_duration=format_timedelta(subscription_duration),
    )
    full_context = {**asdict(context), **extra_jinja_context}
    email_content = EMAIL_JINJA_ENVIRONMENT.get_template(template_name).render(full_context)

    from_sender = From("backend@axleos.com", "axleOS.com backend")
    message = Mail(
        from_email=from_sender,
        subject=subject,
        html_content=email_content,
    )
    personalization = Personalization()
    personalization.add_to(To(to_user.user_email))
    message.add_personalization(personalization)

    sendgrid_client = get_sendgrid_client()
    sendgrid_response = sendgrid_client.send(message)
    _logger.info(f"Response from SendGrid: {sendgrid_response}")
