from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

ALL_AVAILABLE: AvailabilityStatus
ALL_UNAVAILABLE: AvailabilityStatus
AUDIO_CAPTURE_UNAVAILABLE: AvailabilityStatus
DESCRIPTOR: _descriptor.FileDescriptor

class Availability(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: AvailabilityStatus
    def __init__(self, status: _Optional[_Union[AvailabilityStatus, str]] = ...) -> None: ...

class Color(_message.Message):
    __slots__ = ["rgba_color"]
    RGBA_COLOR_FIELD_NUMBER: _ClassVar[int]
    rgba_color: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, rgba_color: _Optional[_Iterable[int]] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class AvailabilityStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
