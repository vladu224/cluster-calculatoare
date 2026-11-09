import logging
from concurrent import futures

import grpc

from auth_client import auth_pb2_grpc
from app.config import settings
from app.servicer import AuthServicer


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthServicer(), server)
    server.add_insecure_port(f"[::]:{settings.grpc_port}")
    server.start()
    logging.info("Auth gRPC server listening on port %s", settings.grpc_port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve()