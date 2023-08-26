from functools import lru_cache

from google.cloud.firestore import Client


@lru_cache(maxsize=None)
def get_firestore_client() -> Client:
    client = Client()
    return client
