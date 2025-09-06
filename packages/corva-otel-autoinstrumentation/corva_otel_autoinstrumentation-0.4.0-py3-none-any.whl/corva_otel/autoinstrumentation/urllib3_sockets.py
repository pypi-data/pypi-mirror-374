import uuid
from functools import wraps

from opentelemetry import trace
from urllib3.connection import HTTPConnection, HTTPSConnection


def skip_if_already_patched(func):
    @wraps(func)
    def wrapper(connection_cls, *args, **kwargs):
        if getattr(connection_cls, "_is_socket_patch_applied", False):
            return None

        result = func(connection_cls, *args, **kwargs)
        setattr(connection_cls, "_is_socket_patch_applied", True)
        return result

    return wrapper


@skip_if_already_patched
def _patch_connection_cls(connection_cls, capture_socket_id: bool, capture_socket_requests_count: bool) -> None:
    orig_request = connection_cls.request

    def request(self, method, url, body=None, headers=None, **kwargs):
        span = trace.get_current_span()
        resp = orig_request(self, method, url, body=body, headers=headers, **kwargs)

        if span and span.is_recording():

            if capture_socket_id:
                if not hasattr(self, "_corva_socket_id"):
                    self._corva_socket_id = str(uuid.uuid4())
                span.set_attribute("x.net.socket.id", self._corva_socket_id)

            if capture_socket_requests_count:
                if not hasattr(self, "_corva_socket_req_count"):
                    self._corva_socket_req_count = 0
                self._corva_socket_req_count += 1
                span.set_attribute("x.net.socket.requests_count", self._corva_socket_req_count)

        return resp

    connection_cls.request = request


def patch_urllib3_connection_classes(
    capture_socket_id: bool = False,
    capture_socket_requests_count: bool = False
) -> None:
    _patch_connection_cls(HTTPConnection, capture_socket_id, capture_socket_requests_count)
    _patch_connection_cls(HTTPSConnection, capture_socket_id, capture_socket_requests_count)
