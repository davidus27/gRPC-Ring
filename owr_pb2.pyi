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

class election_request(_message.Message):
    __slots__ = ["direction", "node_id"]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    direction: int
    node_id: int
    def __init__(self, node_id: _Optional[int] = ..., direction: _Optional[int] = ...) -> None: ...

class election_response(_message.Message):
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

class termination_request(_message.Message):
    __slots__ = ["terminating_node_id"]
    TERMINATING_NODE_ID_FIELD_NUMBER: _ClassVar[int]
    terminating_node_id: int
    def __init__(self, terminating_node_id: _Optional[int] = ...) -> None: ...

class termination_response(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
