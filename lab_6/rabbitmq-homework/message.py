from dataclasses import dataclass
from enum import Enum


class SenderType(Enum):
    CREW = "crew"
    SUPPLIER = "supplier"
    ADMIN = "admin"


@dataclass
class Message:
    sender: str
    sender_type: SenderType
    body: str

    def to_dict(self) -> dict:
        return {"sender": self.sender, "sender_type": self.sender_type.name, "body": self.body}
