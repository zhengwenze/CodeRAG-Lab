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

# 复制整个项目结构
COPY ../server/src/ /app/src/
COPY ../pyproject.toml /app/

# 安装依赖
RUN pip install --no-cache-dir -e .

RUN mkdir -p /app/logs /app/data

EXPOSE 8000

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "coderag.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
