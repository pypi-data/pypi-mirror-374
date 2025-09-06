import logging
from os import environ

from opentelemetry.sdk._logs import LoggingHandler

_otel_log_sending_level_map = {
    "critical": logging.CRITICAL,
    "fatal": logging.FATAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "warn": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
    "notset": logging.NOTSET,
    "all": logging.NOTSET
}

def initialize():
    # Instrument logging with OpenTelemetry
    # original experimental env var
    # https://github.com/open-telemetry/opentelemetry-python/blob/8fbfc3713e6925ed69b411468694734461065a8f/
    # opentelemetry-sdk/src/opentelemetry/sdk/_configuration/__init__.py#L399-L409
    OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED = environ.get(
        "OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED", "true"
    ).lower() in ["true", "yes", "1"]

    # Corva custom env var
    otel_log_sending_disabled = environ.get(
        "OTEL_X_LOG_SENDING_DISABLED",
        str(not OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED)
    ).lower() not in ["true", "yes", "1"]

    # align the original env var
    environ["OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED"] = str(otel_log_sending_disabled)

def set_log_sending_level():
    otel_log_sending_level = environ.get(
        "OTEL_X_LOG_SENDING_LEVEL", ""
    ).lower()

    log_level = _otel_log_sending_level_map.get(otel_log_sending_level)

    if log_level is not None:
        for handler in logging.getLogger().handlers:
            if isinstance(handler, LoggingHandler):
                handler.setLevel(log_level)
