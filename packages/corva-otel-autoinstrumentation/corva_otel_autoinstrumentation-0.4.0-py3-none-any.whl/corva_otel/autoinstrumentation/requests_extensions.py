from os import environ

from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.trace import Span
import requests

from .urllib3_sockets import patch_urllib3_connection_classes


# Function to calculate the size of a request
def calculate_request_sizes(prepared_request: requests.PreparedRequest):
    # Calculate the header size
    header_bytes = sum(len(key) + len(value) for key, value in prepared_request.headers.items())

    # Calculate body size (if present)
    body_bytes = len(prepared_request.body or b"")

    # Total request size
    total_bytes = header_bytes + body_bytes
    return total_bytes, header_bytes, body_bytes

# Function to calculate the size of a response
def calculate_response_sizes(response: requests.Response):
    # Calculate header size
    header_bytes = sum(len(key) + len(value) for key, value in response.headers.items())

    # Calculate body size (if present and readable)
    body_bytes = len(response.content or b"")

    # Total response size
    total_bytes = header_bytes + body_bytes
    return total_bytes, header_bytes, body_bytes

# Hook to collect request bytes from the request
def request_hook(span: Span, request: requests.PreparedRequest):
    if span.is_recording():
        total_bytes, header_bytes, body_bytes = calculate_request_sizes(request)
        span.set_attribute("http.request.total_bytes", total_bytes)
        span.set_attribute("http.request.header_bytes", header_bytes)
        span.set_attribute("http.request.body_bytes", body_bytes)

# Hook to collect response bytes from the response
def response_hook(span: Span, request: requests.PreparedRequest, response: requests.Response):
    if span.is_recording():
        total_bytes, header_bytes, body_bytes = calculate_response_sizes(response)
        span.set_attribute("http.response.total_bytes", total_bytes)
        span.set_attribute("http.response.header_bytes", header_bytes)
        span.set_attribute("http.response.body_bytes", body_bytes)

def initialize():
    # Instrument requests with OpenTelemetry and add hooks

    capture_request_bytes = environ.get(
        "OTEL_X_PYTHON_INSTRUMENTATION_REQUESTS_CAPTURE_REQUEST_BYTES", "true"
    ).lower() in ["true", "yes", "1"]

    capture_response_bytes = environ.get(
        "OTEL_X_PYTHON_INSTRUMENTATION_REQUESTS_CAPTURE_RESPONSE_BYTES", "true"
    ).lower() in ["true", "yes", "1"]

    capture_socket_id = environ.get(
        "OTEL_X_PYTHON_INSTRUMENTATION_REQUESTS_CAPTURE_SOCKET_ID", "true"
    ).lower() in ["true", "yes", "1"]

    capture_socket_requests_count = environ.get(
        "OTEL_X_PYTHON_INSTRUMENTATION_REQUESTS_CAPTURE_SOCKET_REQUESTS_COUNT", "true"
    ).lower() in ["true", "yes", "1"]

    if capture_request_bytes or capture_response_bytes:
        # NOTE: Triggers warning `Attempting to instrument while already instrumented`, that is harmless in this case
        RequestsInstrumentor().instrument(
            request_hook=request_hook if capture_request_bytes else None,
            response_hook=response_hook if capture_response_bytes else None
        )

    if capture_socket_id or capture_socket_requests_count:
        patch_urllib3_connection_classes(capture_socket_id, capture_socket_requests_count)
