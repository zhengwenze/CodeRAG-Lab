# ===========================================
# CodeRAG Lab Makefile
# ===========================================
# 快速开始:
#   make install    - 安装依赖
#   make run        - 启动开发服务器
#   make test       - 运行测试
#   make lint       - 代码检查
#   make format     - 格式化代码
#   make clean      - 清理构建产物
# ===========================================

PYTHON=python3
PIP=pip3
SRC_DIR=server/src
TEST_DIR=tests

# 虚拟环境
VENV=.venv
VENV_ACTIVATE=$(VENV)/bin/activate

# 目标
.PHONY: all install run test lint eval format clean help

all: install

# 安装依赖
install:
	$(PIP) install -e .[dev]

# 启动开发服务器
run:
	$(PYTHON) -m uvicorn $(SRC_DIR).coderag.api.main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
test:
	$(PYTHON) -m pytest $(TEST_DIR) -v

# 代码检查
lint:
	$(PYTHON) -m ruff check $(SRC_DIR)
	$(PYTHON) -m black --check $(SRC_DIR)

# 格式化代码
format:
	$(PYTHON) -m ruff format $(SRC_DIR)
	$(PYTHON) -m black $(SRC_DIR)

# 运行评测
eval:
	$(PYTHON) -m $(SRC_DIR).coderag.eval.runner

# 清理
clean:
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf $(SRC_DIR)/**/__pycache__
	rm -rf $(TEST_DIR)/**/__pycache__
	rm -rf data/runs/*
	rm -rf logs/*
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/

# 帮助
help:
	@echo "CodeRAG Lab 开发命令:"
	@echo "  make install   - 安装依赖"
	@echo "  make run       - 启动开发服务器 (http://localhost:8000)"
	@echo "  make test      - 运行测试"
	@echo "  make lint      - 代码检查"
	@echo "  make format    - 格式化代码"
	@echo "  make eval      - 运行评测"
	@echo "  make clean     - 清理构建产物"
