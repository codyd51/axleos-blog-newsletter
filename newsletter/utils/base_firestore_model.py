from abc import ABC
from typing import ClassVar

import pydantic


class FirestoreModel(ABC, pydantic.BaseModel):
    # The Pydantic field to be used to store and pass around the document's Firestore ID/reference
    _ID_FIELD: ClassVar[str]
