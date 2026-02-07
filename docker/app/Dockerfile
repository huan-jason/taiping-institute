# syntax=docker/dockerfile:1

## -----------------------------------------------------
FROM dhi.io/python:3-alpine3.23-dev AS build-stage

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/venv/bin:$PATH"

WORKDIR /

COPY requirements.txt .

RUN python -m venv /venv \
    && source /venv/bin/activate \
    && pip install --no-cache-dir --requirement requirements.txt

## -----------------------------------------------------
FROM dhi.io/python:3-alpine3.23 AS runtime-stage

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/venv/bin:$PATH"

WORKDIR /app

COPY --from=build-stage /venv /venv
COPY --from=build-stage /bin/sleep /bin/

ENTRYPOINT ["/venv/bin/daphne"]
cmd ["--bind", "0.0.0.0", "project.asgi:application"]
