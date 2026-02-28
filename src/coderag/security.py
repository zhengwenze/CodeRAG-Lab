import re
import html
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json


class InputValidator:
    """输入验证器 - 防止注入攻击"""

    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'eval\s*\(',
        r'exec\s*\(',
        r'\$\{',
        r'__import__',
    ]

    MAX_LENGTHS = {
        'message': 10000,
        'question': 5000,
        'repo_path': 1000,
        'file_path': 1000,
    }

    @classmethod
    def sanitize_string(cls, value: str, field_name: str = 'input') -> str:
        """清理字符串输入"""
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")

        sanitized = value.strip()

        if len(sanitized) > cls.MAX_LENGTHS.get(field_name, 10000):
            raise ValueError(f"{field_name} exceeds maximum length of {cls.MAX_LENGTHS.get(field_name, 10000)}")

        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError(f"{field_name} contains potentially dangerous content")

        return sanitized

    @classmethod
    def validate_message(cls, message: str) -> str:
        """验证聊天消息"""
        return cls.sanitize_string(message, 'message')

    @classmethod
    def validate_question(cls, question: str) -> str:
        """验证问题"""
        return cls.sanitize_string(question, 'question')

    @classmethod
    def validate_repo_path(cls, path: str) -> str:
        """验证代码库路径"""
        sanitized = cls.sanitize_string(path, 'repo_path')

        dangerous_chars = ['..', '~', '$', '`', '|', ';', '&', '>', '<']
        for char in dangerous_chars:
            if char in sanitized:
                raise ValueError(f"repo_path contains dangerous character: {char}")

        return sanitized

    @classmethod
    def validate_file_path(cls, path: str) -> str:
        """验证文件路径"""
        sanitized = cls.sanitize_string(path, 'file_path')

        if sanitized.startswith('/') or '..' in sanitized:
            raise ValueError("file_path must be a relative path")

        return sanitized

    @classmethod
    def validate_json(cls, data: Any, max_size: int = 1024 * 1024) -> Any:
        """验证 JSON 数据"""
        if isinstance(data, dict):
            json_str = json.dumps(data)
            if len(json_str) > max_size:
                raise ValueError(f"JSON data exceeds maximum size of {max_size} bytes")
            return data
        raise ValueError("Data must be a valid JSON object")

    @classmethod
    def validate_temperature(cls, temperature: float) -> float:
        """验证温度参数"""
        if not isinstance(temperature, (int, float)):
            raise ValueError("temperature must be a number")
        if temperature < 0 or temperature > 2:
            raise ValueError("temperature must be between 0 and 2")
        return float(temperature)

    @classmethod
    def validate_top_k(cls, top_k: int) -> int:
        """验证 top_k 参数"""
        if not isinstance(top_k, int):
            raise ValueError("top_k must be an integer")
        if top_k < 1 or top_k > 100:
            raise ValueError("top_k must be between 1 and 100")
        return top_k


class OutputSanitizer:
    """输出清理器 - 防止 XSS 等安全问题"""

    @classmethod
    def sanitize_output(cls, text: str) -> str:
        """清理输出文本"""
        if not isinstance(text, str):
            return str(text)

        sanitized = html.escape(text)

        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', sanitized)

        return sanitized

    @classmethod
    def sanitize_source(cls, source: Dict[str, Any]) -> Dict[str, Any]:
        """清理来源信息"""
        if not isinstance(source, dict):
            return {}

        return {
            'file': cls.sanitize_output(source.get('file', '')),
            'chunk_id': source.get('chunk_id', ''),
            'score': source.get('score', 0.0),
        }

    @classmethod
    def sanitize_response(cls, response: Dict[str, Any]) -> Dict[str, Any]:
        """清理响应数据"""
        if not isinstance(response, dict):
            return {}

        sanitized = {}

        if 'answer' in response:
            sanitized['answer'] = cls.sanitize_output(response['answer'])

        if 'sources' in response:
            sources = response['sources']
            if isinstance(sources, list):
                sanitized['sources'] = [cls.sanitize_source(s) for s in sources]
            else:
                sanitized['sources'] = []

        if 'message' in response:
            sanitized['message'] = cls.sanitize_output(response['message'])

        for key, value in response.items():
            if key not in sanitized:
                sanitized[key] = value

        return sanitized


def get_input_validator() -> InputValidator:
    """获取输入验证器实例"""
    return InputValidator()


def get_output_sanitizer() -> OutputSanitizer:
    """获取输出清理器实例"""
    return OutputSanitizer()
