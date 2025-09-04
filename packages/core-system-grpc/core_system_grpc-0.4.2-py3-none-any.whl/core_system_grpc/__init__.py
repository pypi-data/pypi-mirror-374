"""Core System gRPC Package"""


def test_simple_function():
    """간단한 테스트 함수"""
    print("Hello from core-system-grpc package!")
    return "Success"


try:
    from core_system_grpc.services.product_service_pb2_grpc import ProductServiceStub
    from core_system_grpc.messages.product.request_pb2 import GetProductsByShopRequest
    from core_system_grpc.messages.common.pagination_pb2 import PaginationRequest
except ImportError:
    # Fallback for when package is not installed
    pass

__version__ = "0.2.58"

__all__ = [
    "ProductServiceStub",
    "GetProductsByShopRequest",
    "PaginationRequest",
    "test_simple_function",
]
