import json
import logging

import falcon
from models.subscribed_users import (
    SubscribedUser,
    get_subscribed_users_collection
)
from pydantic import BaseModel
from utils.api import parse_get_parameters
from utils.email import send_email

_logger = logging.getLogger(__name__)


class UnsubscribeEmailRequest(BaseModel):
    email: str


class UnsubscribeEmailResource:
    def on_get(self, request: falcon.Request, response: falcon.Response) -> None:
        # Set our response upfront, so we don't have to worry about it on early-return paths
        # This is purely to help the user see that something happened
        response.text = "Unsubscribe successful"

        # PT: This endpoint is implemented with a GET so that it can be embedded as a link, though conceptually a
        # different method would be more appropriate.
        unsubscribe_info = parse_get_parameters(request, UnsubscribeEmailRequest)
        client_ip = request.remote_addr
        _logger.info(f"Unsubscribing email on behalf of {client_ip}: {unsubscribe_info}")

        # Reject an empty email
        if not unsubscribe_info.email:
            _logger.info(f"Rejecting empty email")
            raise falcon.HTTPBadRequest(description="An empty email isn't valid")

        document_ref = get_subscribed_users_collection().document(unsubscribe_info.email)
        document_snap = document_ref.get()
        if not document_snap.exists:
            _logger.error(f"Tried to unsubscribe a user that's not subscribed: {unsubscribe_info}")
            return

        user_record = SubscribedUser.from_snapshot(document_snap)
        document_ref.delete()

        # Inform the user they've been successfully unsubscribed
        send_email(
            to_user=user_record,
            subject="You've been unsubscribed from https://axleos.com/blog",
            template_name="unsubscribe.html.jinja2",
            # No need to include an unsubscribe button
            should_include_unsubscribe_button=False,
        )
