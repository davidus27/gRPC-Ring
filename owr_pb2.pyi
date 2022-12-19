from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class aliveRequest(_message.Message):
    __slots__ = ["nodeid"]
    NODEID_FIELD_NUMBER: _ClassVar[int]
    nodeid: int
    def __init__(self, nodeid: _Optional[int] = ...) -> None: ...

class aliveResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class owrRequest(_message.Message):
    __slots__ = ["content", "receiverid", "senderid"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    RECEIVERID_FIELD_NUMBER: _ClassVar[int]
    SENDERID_FIELD_NUMBER: _ClassVar[int]
    content: str
    receiverid: int
    senderid: int
    def __init__(self, receiverid: _Optional[int] = ..., senderid: _Optional[int] = ..., content: _Optional[str] = ...) -> None: ...

class owrResponse(_message.Message):
    __slots__ = ["code"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: int
    def __init__(self, code: _Optional[int] = ...) -> None: ...
