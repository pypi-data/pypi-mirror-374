from typing import Annotated

from fastapi import FastAPI
from prometheus_client import CollectorRegistry
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field


class PrometheusConfig(BaseModel):
    exclude_handlers: Annotated[list[str], Field(default_factory=list)]


def instrument(
        app: FastAPI, config: PrometheusConfig, registry: CollectorRegistry
) -> None:
    prometheus = Instrumentator(
        registry=registry,
        excluded_handlers=config.exclude_handlers,
    )
    prometheus.instrument(app)
    prometheus.expose(app)
