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
from utils.email import send_email
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

        # Inform the user they've been successfully subscribed
        # Note that the subscription duration will be zero in this case, but that's kind of fun...
        send_email(
            to_user=newly_subscribed_user,
            subject="You've been subscribed to https://axleos.com/blog",
            template_name="subscribe.html.jinja2",
        )

        response.text = json.dumps({})
