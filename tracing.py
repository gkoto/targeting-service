"""
Módulo de inicialização do OpenTelemetry para microsserviços Python.
Copie este arquivo para a raiz de cada serviço Python.

Usa SDKs OTel (requisito do projeto) e envia pro OTel Collector,
que roteia traces pro Datadog Agent.
"""
import os
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

log = logging.getLogger(__name__)


def init_telemetry(app, service_name):
    """Inicializa OpenTelemetry com export via OTLP pro OTel Collector."""

    otel_endpoint = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4317"
    )

    resource = Resource.create({
        "service.name": service_name,
        "service.namespace": "togglemaster",
        "deployment.environment": os.getenv("ENVIRONMENT", "production"),
    })

    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=otel_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()

    log.info(f"OpenTelemetry inicializado para {service_name} -> {otel_endpoint}")
