from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

AVAILABLE: AvailabilityStatus
DESCRIPTOR: _descriptor.FileDescriptor
UNAVAILABLE: AvailabilityStatus

class AudioPacket(_message.Message):
    __slots__ = ["captured_audio", "num_frames", "timestamp"]
    CAPTURED_AUDIO_FIELD_NUMBER: _ClassVar[int]
    NUM_FRAMES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    captured_audio: bytes
    num_frames: int
    timestamp: int
    def __init__(self, timestamp: _Optional[int] = ..., num_frames: _Optional[int] = ..., captured_audio: _Optional[bytes] = ...) -> None: ...

class Availability(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: AvailabilityStatus
    def __init__(self, status: _Optional[_Union[AvailabilityStatus, str]] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ProcessToCapture(_message.Message):
    __slots__ = ["pid"]
    PID_FIELD_NUMBER: _ClassVar[int]
    pid: int
    def __init__(self, pid: _Optional[int] = ...) -> None: ...

class AvailabilityStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
