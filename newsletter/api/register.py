import json
import logging

import falcon
from pydantic import BaseModel

from newsletter.utils.api import parse_json_body

_logger = logging.getLogger(__name__)


class RegisterEmailRequest(BaseModel):
    email: str


class RegisterEmailResource:
    def on_post(self, request: falcon.Request, response: falcon.Response) -> None:
        registration_info = parse_json_body(request, RegisterEmailRequest)
        client_ip = request.remote_addr
        _logger.info(f'Registering email on behalf of {client_ip}: {registration_info}')

        response.text = json.dumps({})
