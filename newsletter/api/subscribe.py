import json
import logging
import datetime

import falcon
from pydantic import BaseModel
import google.api_core.exceptions
from sendgrid import Mail
from sendgrid import Personalization
from sendgrid import To

from clients.neutrino import NeutrinoEmailValidityEnum
from clients.neutrino import get_neutrino_client
from clients.sendgrid import get_sendgrid_client
from models.subscribed_users import SubscribedUser
from models.subscribed_users import get_subscribed_users_collection
from newsletter.utils.api import parse_json_body
from templates import EMAIL_JINJA_ENVIRONMENT
from utils.timedelta import format_timedelta

_logger = logging.getLogger(__name__)


class SubscribeEmailRequest(BaseModel):
    email: str


class SubscribeEmailResource:
    def on_post(self, request: falcon.Request, response: falcon.Response) -> None:
        subscription_info = parse_json_body(request, SubscribeEmailRequest)
        client_ip = request.remote_addr
        _logger.info(f'Subscribing email on behalf of {client_ip}: {subscription_info}')


        # First, call out to Neutrino to check whether the email is valid
        email_validity = get_neutrino_client().check_email_validity(subscription_info.email)
        _logger.info(f'Neutrino result for {subscription_info.email}: {email_validity}')
        if email_validity not in [NeutrinoEmailValidityEnum.VALID]:
            raise falcon.HTTPBadRequest(description="Neutrino says this email is invalid")

        # All good - save the email
        newly_subscribed_user = SubscribedUser(
            user_email=subscription_info.email,
            signup_ip=client_ip,
            date_created=datetime.datetime.utcnow(),
        )
        user_ref = newly_subscribed_user.get_reference(get_subscribed_users_collection())

        try:
            user_ref.create(newly_subscribed_user.dict())
        except google.api_core.exceptions.AlreadyExists:
            _logger.error(f'Ignoring request to subscribe {subscription_info} because they\'re already subscribed')

        # Send the user an email indicating that they've just been registered
        now = datetime.datetime.utcnow()
        # The subscription duration will be zero...
        subscription_duration = now - newly_subscribed_user.date_created
        context = {
            # TODO(PT): Dynamically generate these colors
            "background_color": "rgb(254, 255, 252)",
            "border_color": "rgb(197, 198, 195)",
            "generated_at": now.strftime("%B %d, %Y at %H:%M"),
            "user_email": newly_subscribed_user.user_email,
            "subscription_duration": format_timedelta(subscription_duration),
            "title": "Welcome!",
        }
        email_content = EMAIL_JINJA_ENVIRONMENT.get_template("new_subscriber.html.jinja2").render(context)

        message = Mail(
            from_email='backend@axleos.com',
            subject='You\'ve been subscribed to https://axleos.com/blog',
            html_content=email_content,
        )
        personalization = Personalization()
        personalization.add_to(To(newly_subscribed_user.user_email))
        message.add_personalization(personalization)

        sendgrid_client = get_sendgrid_client()
        sendgrid_response = sendgrid_client.send(message)
        _logger.info(f"Response from welcome email: {sendgrid_response}")

        response.text = json.dumps({})
