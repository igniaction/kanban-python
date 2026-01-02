FROM python:3.11-bookworm

RUN apt-get update \
 && apt-get install -y --no-install-recommends make docker.io \
 && rm -rf /var/lib/apt/lists/*

# ruff/pytest para lint/test do seu Makefile
RUN python -m pip install --no-cache-dir -U pip \
 && pip install --no-cache-dir ruff pytest
