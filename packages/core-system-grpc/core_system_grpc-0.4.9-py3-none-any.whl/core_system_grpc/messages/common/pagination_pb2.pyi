from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PaginationRequest(_message.Message):
    __slots__ = ["limit", "offset"]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    limit: int
    offset: int
    def __init__(self, offset: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class PaginationResponse(_message.Message):
    __slots__ = ["limit", "offset", "total_count"]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    limit: int
    offset: int
    total_count: int
    def __init__(self, total_count: _Optional[int] = ..., offset: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...
