from messages.common import pagination_pb2 as _pagination_pb2
from messages.common import search_pb2 as _search_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetProductsByShopRequest(_message.Message):
    __slots__ = ["embed", "fields", "filters", "order_by", "pagination", "search", "shop_id"]
    EMBED_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    SEARCH_FIELD_NUMBER: _ClassVar[int]
    SHOP_ID_FIELD_NUMBER: _ClassVar[int]
    embed: str
    fields: str
    filters: str
    order_by: str
    pagination: _pagination_pb2.PaginationRequest
    search: _search_pb2.SearchRequest
    shop_id: int
    def __init__(self, shop_id: _Optional[int] = ..., pagination: _Optional[_Union[_pagination_pb2.PaginationRequest, _Mapping]] = ..., search: _Optional[_Union[_search_pb2.SearchRequest, _Mapping]] = ..., fields: _Optional[str] = ..., embed: _Optional[str] = ..., filters: _Optional[str] = ..., order_by: _Optional[str] = ...) -> None: ...
