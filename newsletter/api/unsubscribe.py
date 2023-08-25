import json
import logging
import datetime

import falcon
from pydantic import BaseModel

from models.subscribed_users import SubscribedUser
from models.subscribed_users import get_subscribed_users_collection
from utils.api import parse_get_parameters

_logger = logging.getLogger(__name__)


class UnsubscribeEmailRequest(BaseModel):
    email: str


class UnsubscribeEmailResource:
    def on_get(self, request: falcon.Request, response: falcon.Response) -> None:
        # PT: This endpoint is implemented with a GET so that it can be embedded as a link, though conceptually a
        # different method would be more appropriate.
        unsubscribe_info = parse_get_parameters(request, UnsubscribeEmailRequest)
        client_ip = request.remote_addr
        _logger.info(f'Unsubscribing email on behalf of {client_ip}: {unsubscribe_info}')

        document_ref = get_subscribed_users_collection().document(unsubscribe_info.email)
        if document_ref.get().exists:
            document_ref.delete()
        else:
            _logger.error(f"Tried to unsubscribe a user that's not subscribed: {unsubscribe_info}")

        response.text = json.dumps({})
