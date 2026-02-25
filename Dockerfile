FROM python:3.9-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

RUN pip install --no-cache-dir -e .

COPY src/ /app/src/
COPY data/ /app/data/

RUN mkdir -p /app/logs

EXPOSE 8000

CMD ["uvicorn", "src.coderag.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
