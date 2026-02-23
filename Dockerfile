FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml .

# 安装Python依赖
RUN pip install --no-cache-dir -e .[dev]

# 复制代码
COPY src/ /app/src/

# 复制数据目录
COPY data/ /app/data/

# 暴露端口
EXPOSE 8000

# 运行服务
CMD ["uvicorn", "src.coderag.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]