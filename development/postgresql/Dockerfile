FROM postgres:17

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    wget \
    htop \
    make \
    gcc \
    postgresql-server-dev-17 \
    postgresql-17-wal2json \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*