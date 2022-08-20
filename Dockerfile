ARG PYTHON_VERSION

LABEL org.opencontainers.image.source="https://github.com/michel-tricot/abcon"

FROM python:${PYTHON_VERSION}-slim

RUN \
    apt-get update && \
    apt-get install -y curl git && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /app
COPY . /app

WORKDIR /stage

ENV ENV_PATH="/dev/null"
ENV ABCON_URL="file:///app/_abcon"
ENV ABCON_PACKAGE="/app"
ENV VENV_PATH="build/.venv_docker"

ENTRYPOINT ["/app/abcon"]
