import logging
from pathlib import Path

import falcon
from falcon_cors import CORS
from falcon_cors import CORSMiddleware

from api.subscribe import SubscribeEmailResource
from api.unsubscribe import UnsubscribeEmailResource

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)

app = falcon.App(
    middleware=[
        CORSMiddleware(
            CORS(
                allow_all_origins=True,
                allow_headers_list=["Authorization", "Content-Type"],
                allow_all_methods=True,
                # 1 day but most browsers only allow 10 minutes max
                max_age=86400,
            ),
            default_enabled=False,
        ),
    ]
)

app.add_static_route("/static", (Path(__file__).parents[1] / "templates").as_posix())

app.add_route('/subscribe', SubscribeEmailResource())
app.add_route('/unsubscribe', UnsubscribeEmailResource())
