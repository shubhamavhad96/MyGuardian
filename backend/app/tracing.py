import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "guardrail-api")


def setup_tracer(service_name: str = SERVICE_NAME):
    provider = TracerProvider(
        resource=Resource.create({"service.name": service_name}))
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT",
                         "http://localhost:4318/v1/traces")

    try:
        exporter = OTLPSpanExporter(
            endpoint=endpoint,
            headers={}
        )
        processor = BatchSpanProcessor(exporter)
    except Exception:
        exporter = ConsoleSpanExporter()
        processor = BatchSpanProcessor(exporter)

    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)
