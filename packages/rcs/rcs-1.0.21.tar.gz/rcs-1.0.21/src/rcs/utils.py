from .core import parse_obj_as
from typing import Union
from .types import (
    InboundActionMessage,
    InboundLocationMessage,
    InboundMediaMessage,
    InboundTextMessage,
    InboundMessage,
)


def parse_inbound(
    data: dict,
) -> Union[
    InboundActionMessage,
    InboundTextMessage,
    InboundLocationMessage,
    InboundMediaMessage,
]:
    inbound_msg = parse_obj_as(InboundMessage, data)
    msg_type = inbound_msg.message_type
    if msg_type == "action":
        return parse_obj_as(InboundActionMessage, data)
    elif msg_type == "location":
        return parse_obj_as(InboundLocationMessage, data)
    elif msg_type == "media":
        return parse_obj_as(InboundMediaMessage, data)
    elif msg_type == "text":
        return parse_obj_as(InboundTextMessage, data)
    else:
        raise ValueError(f"Unknown message type: {msg_type}")
