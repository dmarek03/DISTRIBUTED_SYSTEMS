from dataclasses import dataclass
from datetime import datetime
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
        return {
            "sender": self.sender,
            "sender_type": self.sender_type.name,
            "body": self.body,
        }


def format_log(sender_type, sender, routing_key, message, direction="RECEIVED"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"[{timestamp}] [{direction}] [{routing_key}] "
        f"From {sender_type}:{sender} – {message}"
    )
