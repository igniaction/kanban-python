FROM python:3.11-bookworm

RUN apt-get update \
 && apt-get install -y --no-install-recommends make git docker.io \
 && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir -U pip \
 && pip install --no-cache-dir ruff pytest
