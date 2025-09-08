from fastapi import FastAPI
from prometheus_client import CollectorRegistry
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel


class PrometheusConfig(BaseModel):
    exclude_handlers: list[str]


def instrument(
    app: FastAPI, config: PrometheusConfig, registry: CollectorRegistry
) -> None:
    prometheus = Instrumentator(
        registry=registry,
        excluded_handlers=config.exclude_handlers,
    )
    prometheus.instrument(app)
    prometheus.expose(app)
