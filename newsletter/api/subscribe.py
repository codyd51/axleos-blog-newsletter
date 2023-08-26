import datetime
import json
import logging

import falcon
from clients.neutrino import NeutrinoEmailValidityEnum, get_neutrino_client
from models.subscribed_users import (
    SubscribedUser,
    get_subscribed_users_collection
)
from pydantic import BaseModel
from utils.email import send_email

from newsletter.utils.api import parse_json_body

_logger = logging.getLogger(__name__)


class SubscribeEmailRequest(BaseModel):
    email: str


class SubscribeEmailResource:
    def on_post(self, request: falcon.Request, response: falcon.Response) -> None:
        # Set our response upfront, so we don't have to worry about it on early-return paths
        response.text = json.dumps({})

        subscription_info = parse_json_body(request, SubscribeEmailRequest)
        client_ip = request.remote_addr
        _logger.info(f"Subscribing email on behalf of {client_ip}: {subscription_info}")

        # Before doing anything, check whether this user is already subscribed
        subscribed_users_collection = get_subscribed_users_collection()
        maybe_user_ref = subscribed_users_collection.document(subscription_info.email)
        if maybe_user_ref.get().exists:
            _logger.error(f"Ignoring request to subscribe {subscription_info} because they're already subscribed")
            return

        # First, call out to Neutrino to check whether the email is valid
        email_validity = get_neutrino_client().check_email_validity(subscription_info.email)
        _logger.info(f"Neutrino result for {subscription_info.email}: {email_validity}")
        if email_validity not in [NeutrinoEmailValidityEnum.VALID]:
            raise falcon.HTTPBadRequest(description="Neutrino says this email is invalid")

        # All good - save the email
        newly_subscribed_user = SubscribedUser(
            user_email=subscription_info.email,
            signup_ip=client_ip,
            date_created=datetime.datetime.utcnow(),
        )
        user_ref = newly_subscribed_user.get_reference(get_subscribed_users_collection())
        user_ref.create(newly_subscribed_user.dict())

        # Inform the user they've been successfully subscribed
        # Note that the subscription duration will be zero in this case, but that's kind of fun...
        send_email(
            to_user=newly_subscribed_user,
            subject="You've been subscribed to https://axleos.com/blog",
            template_name="subscribe.html.jinja2",
        )
