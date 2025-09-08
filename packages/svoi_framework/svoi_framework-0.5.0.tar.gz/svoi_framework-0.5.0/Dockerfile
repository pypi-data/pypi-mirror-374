FROM python:3.13-slim-bookworm AS final

# add uv & uvx
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -L https://astral.sh/uv/0.8.15/install.sh | sh

ENV PATH="/root/.local/bin/:$PATH"

RUN mkdir /app/

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --group dev --group test --locked --no-install-project

ADD . .

ENTRYPOINT ["/bin/bash", "-c"]