ARG PYTHON_VERSION
ARG BASE_IMAGE

FROM python:${PYTHON_VERSION:-3.13}-${BASE_IMAGE:-slim-bookworm}

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    wget \
    htop \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash pubsubs

COPY --chown=pubsubs:pubsubs ./app /app

USER pubsubs

ARG PIP_ADDITIONAL_REQUIREMENTS

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir ${PIP_ADDITIONAL_REQUIREMENTS}

WORKDIR /app