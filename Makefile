# CodeRAG Lab Makefile

# 环境变量
PYTHON=python3
PIP=pip3
SRC_DIR=src
TEST_DIR=tests

# 虚拟环境
VENV=.venv
VENV_ACTIVATE=$(VENV)\Scripts\activate

# 目标
.PHONY: all install run test lint eval clean

all: install

# 安装依赖
install:
	$(PIP) install -e .[dev]

# 运行服务
run:
	$(PYTHON) -m uvicorn src.coderag.api.main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
 test:
	$(PYTHON) -m pytest $(TEST_DIR) -v

# 运行代码检查
lint:
	$(PYTHON) -m ruff check $(SRC_DIR)
	$(PYTHON) -m black --check $(SRC_DIR)

# 格式化代码
format:
	$(PYTHON) -m ruff format $(SRC_DIR)
	$(PYTHON) -m black $(SRC_DIR)

# 运行评测
eval:
	$(PYTHON) -m src.coderag.eval.runner

# 清理
clean:
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf $(SRC_DIR)\__pycache__
	rm -rf $(TEST_DIR)\__pycache__
	rm -rf data\runs\*