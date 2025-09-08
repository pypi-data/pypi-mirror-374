from fastapi import FastAPI
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as OTLPSpanExporterGRPC,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pydantic import BaseModel


class JaegerConfig(BaseModel):
    grpc_host: str
    service_name: str
    allow_insecure: bool


def instrument(app: FastAPI, config: JaegerConfig) -> None:
    resource = Resource.create()
    tracer = TracerProvider(resource=resource)
    tracer.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporterGRPC(
                endpoint=config.grpc_host,
                insecure=config.allow_insecure,
            )
        )
    )
    FastAPIInstrumentor.instrument_app(app)
