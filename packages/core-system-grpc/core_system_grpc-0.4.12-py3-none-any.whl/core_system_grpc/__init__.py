# -*- coding: utf-8 -*-
"""
Core System gRPC Package

이 패키지는 Core System의 gRPC 서비스와 메시지 정의를 제공합니다.
"""

# Services
from .services.product_service_pb2_grpc import (
    ProductServiceStub,
    ProductServiceServicer,
    ProductService,
    add_ProductServiceServicer_to_server,
)

# Messages - Common
from .messages.common.pagination_pb2 import (
    PaginationRequest,
    PaginationResponse,
)
from .messages.common.search_pb2 import (
    SearchRequest,
    SortRequest,
    SortDirection,
)

# Messages - Product
from .messages.product.common_pb2 import Product
from .messages.product.request_pb2 import GetProductsByShopRequest
from .messages.product.response_pb2 import GetProductsByShopResponse

__version__ = "0.4.11"

__all__ = [
    # Services
    "ProductServiceStub",
    "ProductServiceServicer",
    "ProductService",
    "add_ProductServiceServicer_to_server",
    # Common Messages
    "PaginationRequest",
    "PaginationResponse",
    "SearchRequest",
    "SortRequest",
    "SortDirection",
    # Product Messages
    "Product",
    "GetProductsByShopRequest",
    "GetProductsByShopResponse",
]
