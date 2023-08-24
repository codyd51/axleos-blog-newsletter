import json
import logging
import datetime

import falcon
from pydantic import BaseModel
import google.api_core.exceptions

from models.registered_users import RegisteredUser
from models.registered_users import get_registered_users_collection
from newsletter.utils.api import parse_json_body


_logger = logging.getLogger(__name__)


class RegisterEmailRequest(BaseModel):
    email: str


class RegisterEmailResource:
    def on_post(self, request: falcon.Request, response: falcon.Response) -> None:
        registration_info = parse_json_body(request, RegisterEmailRequest)
        client_ip = request.remote_addr
        _logger.info(f'Registering email on behalf of {client_ip}: {registration_info}')

        newly_registered_user = RegisteredUser(
            user_email=registration_info.email,
            registration_ip=client_ip,
            date_created=datetime.datetime.utcnow(),
        )
        user_ref = newly_registered_user.get_reference(get_registered_users_collection())

        try:
            user_ref.create(newly_registered_user.dict())
        except google.api_core.exceptions.AlreadyExists:
            _logger.error(f'Ignoring request to register {registration_info} because they\'re already registered')

        response.text = json.dumps({})
