import logging

import falcon
from api.send_newsletter import SendNewsletterResource
from api.subscribe import SubscribeEmailResource
from api.unsubscribe import UnsubscribeEmailResource
from falcon_cors import CORS, CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
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
            default_enabled=True,
        ),
    ]
)

app.add_route("/subscribe", SubscribeEmailResource())
app.add_route("/unsubscribe", UnsubscribeEmailResource())
app.add_route("/send_newsletter", SendNewsletterResource())
