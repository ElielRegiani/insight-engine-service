FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY app ./app
COPY integrations ./integrations
COPY prompts ./prompts

RUN useradd --create-home --uid 1000 --user-group appuser && \
    chown -R appuser:appuser /app

FROM base AS dev
USER root
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt && \
    chown -R appuser:appuser /app
USER appuser

FROM base AS runtime
USER appuser

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
