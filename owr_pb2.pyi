from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class alive_request(_message.Message):
    __slots__ = ["nodeid"]
    NODEID_FIELD_NUMBER: _ClassVar[int]
    nodeid: int
    def __init__(self, nodeid: _Optional[int] = ...) -> None: ...

class alive_response(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class owr_request(_message.Message):
    __slots__ = ["content", "receiverid", "senderid", "sending_direction"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    RECEIVERID_FIELD_NUMBER: _ClassVar[int]
    SENDERID_FIELD_NUMBER: _ClassVar[int]
    SENDING_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    content: str
    receiverid: int
    senderid: int
    sending_direction: int
    def __init__(self, receiverid: _Optional[int] = ..., senderid: _Optional[int] = ..., sending_direction: _Optional[int] = ..., content: _Optional[str] = ...) -> None: ...

class owr_response(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
