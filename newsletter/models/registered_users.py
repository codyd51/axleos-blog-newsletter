import datetime
from typing import ClassVar
from google.cloud import firestore_v1

from clients.firestore import get_firestore_client
from utils.base_firestore_model import FirestoreModel


def get_registered_users_collection() -> firestore_v1.collection.CollectionReference:
    return get_firestore_client().collection("registered_users")


class RegisteredUser(FirestoreModel):
    _ID_FIELD: ClassVar[str] = "user_email"

    user_email: str
    registration_ip: str
    date_created: datetime.datetime
