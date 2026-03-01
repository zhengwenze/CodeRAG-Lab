import logging
import os
from logging.handlers import RotatingFileHandler
from coderag.settings import settings


class CustomFormatter(logging.Formatter):
    """自定义日志格式化器"""

    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )

    def format(self, record):
        """格式化日志记录"""
        # 添加上下文信息
        if hasattr(record, 'request_id'):
            self._style._fmt = '%(asctime)s - %(name)s - %(levelname)s - [Request ID: %(request_id)s] - %(message)s'
        else:
            self._style._fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        return super().format(record)


def setup_logging():
    """设置日志系统"""
    # 创建日志目录
    log_dir = os.path.dirname(settings.log_file) if settings.log_file else 'logs'
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))

    # 清除现有处理器
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.log_level))
    console_handler.setFormatter(CustomFormatter())
    root_logger.addHandler(console_handler)

    # 文件处理器
    if settings.log_file:
        file_handler = RotatingFileHandler(
            settings.log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(getattr(logging, settings.log_level))
        file_handler.setFormatter(CustomFormatter())
        root_logger.addHandler(file_handler)

    # 禁用第三方库的日志
    for logger_name in ['urllib3', 'requests', 'qdrant_client']:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)


# 获取日志记录器
def get_logger(name: str = None) -> logging.Logger:
    """获取日志记录器"""
    return logging.getLogger(name)


# 初始化日志系统
setup_logging()