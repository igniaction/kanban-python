FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copia apenas o necessário
COPY server.py database.py /app/
COPY assets /app/assets

# Cria usuário/grupo não-root e prepara /data com permissão
RUN groupadd -g 10001 appuser \
 && useradd -u 10001 -g 10001 -m -s /usr/sbin/nologin appuser \
 && mkdir -p /data \
 && chown -R 10001:10001 /data

EXPOSE 8000

ENV HOST=0.0.0.0
ENV PORT=8000
ENV DB_PATH=/data/kanban.db

USER 10001:10001

CMD ["python", "server.py"]
