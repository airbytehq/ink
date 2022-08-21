ARG PYTHON_VERSION=3.9.0

FROM python:${PYTHON_VERSION}-slim

LABEL org.opencontainers.image.source="https://github.com/michel-tricot/ink"

RUN \
    apt-get update && \
    apt-get install -y curl git && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /app
COPY . /app

WORKDIR /stage

ENV ENV_PATH="/dev/null"
ENV INK_URL="file:///app/_ink"
ENV INK_PACKAGE="/app"
ENV VENV_PATH="build/.venv_docker"

ENTRYPOINT ["/app/ink"]
