from abc import ABC
from typing import ClassVar

import pydantic
from google.cloud import firestore_v1


class FirestoreModel(ABC, pydantic.BaseModel):
    # The Pydantic field to be used to store and pass around the document's Firestore ID/reference
    _ID_FIELD: ClassVar[str]

    @property
    def id(self) -> str:
        firestore_id = getattr(self, self._ID_FIELD)
        return firestore_id

    def get_reference(
        self, collection: firestore_v1.collection.CollectionReference
    ) -> firestore_v1.DocumentReference:
        return collection.document(self.id)
