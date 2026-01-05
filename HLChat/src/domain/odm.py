from datetime import datetime

from odmantic import AIOEngine, Model


class BookModel(Model):
    keyword: str
    publisher: str
    price: int
    image: str

    # Collection Name 지정.
    model_config = {"collection": "books"}

class HLChatRoom(Model):
    room_id: int
    members: list
    created_at: datetime

    model_config = {"collection": "rooms"}

class HLChatMessage(Model):
    room_id: int
    message_ln_no: int
    sender: str
    message: str
    created_at: datetime

    model_config = {"collection": "messages"}

# MongoDB: db -> collection -> document
# MySQL: db -> table -> row
