import pytest
from fastapi.testclient import TestClient
from coderag.api.main import app
from coderag.settings import settings
from coderag.ingest.chunker import Chunker
from coderag.exceptions import InvalidInputException


client = TestClient(app)


def test_health_check():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "0.1.0"


def test_chat_endpoint():
    """测试聊天端点"""
    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": "CodeRAG Lab的核心功能是什么？"}],
            "top_k": 5,
            "stream": True,
            "include_hits": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "message" in data
    assert "references" in data
    assert "retrieval_results" in data
    assert "timestamp" in data


def test_chat_endpoint_invalid_input():
    """测试聊天端点无效输入"""
    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": ""}],
            "top_k": 5,
            "stream": True,
            "include_hits": True,
        },
    )
    # Pydantic validation returns 422 Unprocessable Entity
    assert response.status_code in [400, 422]


def test_chunker_basic():
    """测试分块功能"""
    chunker = Chunker(chunk_size=100, chunk_overlap=20)
    test_content = "a" * 500
    chunks = chunker.chunk_file("test.py", test_content)
    assert len(chunks) > 1
    assert all(len(chunk["content"]) <= 100 for chunk in chunks)


def test_settings_load():
    """测试配置加载"""
    assert settings.project_name == "CodeRAG Lab"
    assert settings.api_port == 8000
    assert settings.vector_store == "qdrant"
    assert settings.top_k == 5


def test_exception_handling():
    """测试异常处理"""
    with pytest.raises(InvalidInputException):
        raise InvalidInputException("Test invalid input")


if __name__ == "__main__":
    pytest.main(["-v", __file__])