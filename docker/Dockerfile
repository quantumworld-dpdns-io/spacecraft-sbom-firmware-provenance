FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements/base.txt .
RUN pip install --user --no-cache-dirs --no-warn-script-location -r base.txt

COPY . .
RUN pip install --user --no-cache-dirs --no-warn-script-location -e .

FROM python:3.11-slim

RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY --from=builder /build/src /app/src
COPY --from=builder /build/alembic /app/alembic
COPY --from=builder /build/alembic.ini /app/alembic.ini

ENV PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app/src:$PYTHONPATH \
    PYTHONUNBUFFERED=1

EXPOSE 8000

USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "sbom_provenance.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
