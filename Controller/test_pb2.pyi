from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class HelloReply(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class SetColorRequest(_message.Message):
    __slots__ = ["rgb_color"]
    RGB_COLOR_FIELD_NUMBER: _ClassVar[int]
    rgb_color: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, rgb_color: _Optional[_Iterable[int]] = ...) -> None: ...
