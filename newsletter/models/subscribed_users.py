import datetime
from typing import ClassVar
from google.cloud import firestore_v1

from clients.firestore import get_firestore_client
from utils.base_firestore_model import FirestoreModel


def get_subscribed_users_collection() -> firestore_v1.collection.CollectionReference:
    return get_firestore_client().collection("subscribed_users")


class SubscribedUser(FirestoreModel):
    _ID_FIELD: ClassVar[str] = "user_email"

    user_email: str
    signup_ip: str
    date_created: datetime.datetime
