import json
import logging
import datetime

import falcon
from pydantic import BaseModel
import google.api_core.exceptions

from models.subscribed_users import SubscribedUser
from models.subscribed_users import get_subscribed_users_collection
from newsletter.utils.api import parse_json_body


_logger = logging.getLogger(__name__)


class SubscribeEmailRequest(BaseModel):
    email: str


class SubscribeEmailResource:
    def on_post(self, request: falcon.Request, response: falcon.Response) -> None:
        subscription_info = parse_json_body(request, SubscribeEmailRequest)
        client_ip = request.remote_addr
        _logger.info(f'Registering email on behalf of {client_ip}: {subscription_info}')

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

        response.text = json.dumps({})
