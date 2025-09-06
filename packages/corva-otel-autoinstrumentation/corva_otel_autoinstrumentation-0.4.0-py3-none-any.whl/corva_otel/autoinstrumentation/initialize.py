import logging
from os import environ, getcwd, pathsep
from os.path import abspath, dirname

import opentelemetry.instrumentation.auto_instrumentation

# This file makes it easy to integrate and initiate OTel SDK via code, similar to how it is done in other languages.
# This way:
#   - it works for different implementations of FaaS (AWS Lambda, OpenFaaS, whatever next ...)
#   - it is a concern of Code Owners not DevOps if and how the code is instrumented, so
#     no Docker / K8S / Command / Scripts need changing, everything works
#     from well-known env vars https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/
#   - it works for multi-workers / threads like `gunicorn`, `uvicorn` etc.
#     cases https://github.com/open-telemetry/opentelemetry-python/issues/3573#issuecomment-1962853105
#
# Sadly OpenTelemetry Python have deviated from all other implementations providing this `opentelemetry-instrument` app
# see https://opentelemetry.io/docs/languages/python/getting-started/#run-the-instrumented-app
# so we need our own implementation

# Optionally initialize OTel, by importing this file first
if environ.get("OTEL_SDK_DISABLED") != "true":
    # Respect OTEL_LOG_LEVEL
    # TODO: Remove this once https://github.com/open-telemetry/opentelemetry-python/issues/1059 is available
    logging.getLogger("opentelemetry").setLevel(environ.get("OTEL_LOG_LEVEL", "info").upper())

    # Instrument packages through prefixed `PYTHONPATH` that includes instrumented packages first
    python_path = environ.get("PYTHONPATH")

    if not python_path:
        python_path = []

    else:
        python_path = python_path.split(pathsep)

    cwd_path = getcwd()

    # This is being added to support applications that are being run from their
    # own executable, like Django.
    # FIXME investigate if there is another way to achieve this
    if cwd_path not in python_path:
        python_path.insert(0, cwd_path)

    filedir_path = dirname(
        abspath(opentelemetry.instrumentation.auto_instrumentation.__file__)
    )

    python_path = [path for path in python_path if path != filedir_path]

    python_path.insert(0, filedir_path)

    environ["PYTHONPATH"] = pathsep.join(python_path)

    # Setup Pymongo instrumentation if available
    # NOTE: Triggers warning `Attempting to instrument while already instrumented`, that is harmless in this case
    try:
        from opentelemetry.instrumentation.pymongo import PymongoInstrumentor

        # TODO: Enable by default ONLY once there is a proper solution of
        #       https://github.com/open-telemetry/opentelemetry-collector/issues/6046
        #       Meanwhile keep it disabled unless needed, to avoid dropping ALL SPANS in a BATCH because of
        #       `Permanent error: rpc error: code = ResourceExhausted desc =
        #       grpc: received message after decompression larger than max (xxxxxxxx vs. 4194304)`
        #       whenever there are spans or batches larger than 4MB static limit of grpc.
        #       If required another workaround could be to use `http`
        #       for `otel-agent` -> `otel-lb` -> `otel-gw` connections.
        capture_statement = environ.get(
            "OTEL_PYTHON_INSTRUMENTATION_PYMONGO_CAPTURE_STATEMENT", ""
        ).lower() in ["true", "yes", "1"]

        PymongoInstrumentor().instrument(capture_statement=capture_statement)
    except ImportError:
        PymongoInstrumentor = None

    try:
        from .requests_extensions import initialize as requests_extensions_initialize
        requests_extensions_initialize()
    except ImportError:
        pass

    try:
        from .logging_extensions import initialize as logging_extensions_initialize
        logging_extensions_initialize()
    except ImportError:
        pass

    # Initialize OTel components via ENV variables
    # (tracer provider, meter provider, logger provider, processors, exporters, etc.)
    from opentelemetry.instrumentation.auto_instrumentation import (  # noqa: F401 I001
        sitecustomize,
    )

    try:
        from .logging_extensions import set_log_sending_level
        set_log_sending_level()
    except ImportError:
        pass
