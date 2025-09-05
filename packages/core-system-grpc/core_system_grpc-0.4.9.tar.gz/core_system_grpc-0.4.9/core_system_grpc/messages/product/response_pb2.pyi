from messages.product import common_pb2 as _common_pb2
from messages.common import pagination_pb2 as _pagination_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetProductsByShopResponse(_message.Message):
    __slots__ = ["pagination", "products"]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    pagination: _pagination_pb2.PaginationResponse
    products: _containers.RepeatedCompositeFieldContainer[_common_pb2.Product]
    def __init__(self, products: _Optional[_Iterable[_Union[_common_pb2.Product, _Mapping]]] = ..., pagination: _Optional[_Union[_pagination_pb2.PaginationResponse, _Mapping]] = ...) -> None: ...
