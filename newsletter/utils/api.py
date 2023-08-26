import json
from typing import Type, TypeVar

import falcon
from pydantic import BaseModel

_BaseModelT = TypeVar("_BaseModelT", bound=BaseModel)


def parse_json_body(request: falcon.Request, body_shape: Type[_BaseModelT]) -> _BaseModelT:
    content = request.bounded_stream.read()
    request_json = json.loads(content)
    parsed_message = body_shape.parse_obj(request_json)
    return parsed_message


def parse_get_parameters(request: falcon.Request, body_shape: Type[_BaseModelT]) -> _BaseModelT:
    parsed_message = body_shape.parse_obj(request.params)
    return parsed_message
