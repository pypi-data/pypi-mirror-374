from langgraph.checkpoint.serde.base import SerializerProtocol
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

SERIALIZER: SerializerProtocol = JsonPlusSerializer()


def set_serializer(serializer: SerializerProtocol) -> None:
    global SERIALIZER
    SERIALIZER = serializer


def get_serializer() -> SerializerProtocol:
    return SERIALIZER
