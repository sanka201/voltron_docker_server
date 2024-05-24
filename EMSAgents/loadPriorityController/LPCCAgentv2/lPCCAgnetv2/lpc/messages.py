from dataclasses import dataclass
from enum import Enum, auto


class MessageType(Enum):
    SWITCH_ON = auto()
    SWITCH_OFF = auto()
    READ = auto()
    WRITE= auto()


@dataclass
class Message:
    device_id: str
    msg_type: MessageType
    control:str
    data: dict