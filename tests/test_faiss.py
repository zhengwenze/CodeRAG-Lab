import pytest
import os
import tempfile
from coderag.rag.faiss_store import FaissStore
from coderag.settings import settings


@pytest.fixture
def faiss_store():
    """创建FAISS存储实例"""
    # 创建临时目录用于测试
    with tempfile.TemporaryDirectory() as temp_dir:
        # 保存原始配置
        original_index_path = settings.faiss_index_path
        original_metadata_path = settings.faiss_metadata_path
        
        # 修改配置为临时目录
        settings.faiss_index_path = os.path.join(temp_dir, "faiss_index")
        settings.faiss_metadata_path = os.path.join(temp_dir, "faiss_metadata.pkl")
        
        try:
            # 创建FAISS存储实例
            store = FaissStore()
            yield store
        finally:
            # 恢复原始配置
            settings.faiss_index_path = original_index_path
            settings.faiss_metadata_path = original_metadata_path


def test_faiss_store_init(faiss_store):
    """测试FAISS存储初始化"""
    assert faiss_store is not None
    assert faiss_store.index is not None
    assert len(faiss_store.metadata) == 0
    assert faiss_store.get_index_size() == 0


def test_faiss_store_add_points(faiss_store):
    """测试添加向量点"""
    # 创建测试向量点
    test_points = [
        {
            'file_path': 'test1.py',
            'content': 'def hello():\n    print("Hello, world!")',
            'embedding': [0.1] * settings.embedding_dim,
            'start_line': 1,
            'end_line': 2,
            'chunk_size': 20,
        },
        {
            'file_path': 'test2.py',
            'content': 'class Test:\n    def __init__(self):\n        self.value = 42',
            'embedding': [0.2] * settings.embedding_dim,
            'start_line': 1,
            'end_line': 3,
            'chunk_size': 30,
        },
    ]
    
    # 添加向量点
    faiss_store.add_points(test_points)
    
    # 验证索引大小
    assert faiss_store.get_index_size() == 2
    assert len(faiss_store.metadata) == 2


def test_faiss_store_search(faiss_store):
    """测试检索功能"""
    # 创建测试向量点
    # 使用不同的向量，确保归一化后也不同
    embedding_dim = settings.embedding_dim
    test_points = [
        {
            'file_path': 'test1.py',
            'content': 'def hello():\n    print("Hello, world!")',
            'embedding': [1.0] + [0.0] * (embedding_dim - 1),  # 第一个元素为1，其余为0
            'start_line': 1,
            'end_line': 2,
            'chunk_size': 20,
        },
        {
            'file_path': 'test2.py',
            'content': 'class Test:\n    def __init__(self):\n        self.value = 42',
            'embedding': [0.0] + [1.0] + [0.0] * (embedding_dim - 2),  # 第二个元素为1，其余为0
            'start_line': 1,
            'end_line': 3,
            'chunk_size': 30,
        },
    ]
    
    # 添加向量点
    faiss_store.add_points(test_points)
    
    # 测试检索
    query_vector = [1.0] + [0.0] * (embedding_dim - 1)  # 与第一个点相似
    results = faiss_store.search(query_vector, top_k=2)
    
    # 验证检索结果
    assert len(results) == 2
    assert results[0]['file_path'] == 'test1.py'  # 第一个结果应该是最相似的
    assert results[0]['rank'] == 1
    assert results[1]['file_path'] == 'test2.py'
    assert results[1]['rank'] == 2


def test_faiss_store_clear_index(faiss_store):
    """测试清空索引"""
    # 创建测试向量点
    test_points = [
        {
            'file_path': 'test1.py',
            'content': 'def hello():\n    print("Hello, world!")',
            'embedding': [0.1] * settings.embedding_dim,
            'start_line': 1,
            'end_line': 2,
            'chunk_size': 20,
        },
    ]
    
    # 添加向量点
    faiss_store.add_points(test_points)
    assert faiss_store.get_index_size() == 1
    
    # 清空索引
    faiss_store.clear_index()
    assert faiss_store.get_index_size() == 0
    assert len(faiss_store.metadata) == 0


def test_faiss_store_persistence():
    """测试索引持久化"""
    # 创建临时目录用于测试
    with tempfile.TemporaryDirectory() as temp_dir:
        # 保存原始配置
        original_index_path = settings.faiss_index_path
        original_metadata_path = settings.faiss_metadata_path
        
        # 修改配置为临时目录
        settings.faiss_index_path = os.path.join(temp_dir, "faiss_index")
        settings.faiss_metadata_path = os.path.join(temp_dir, "faiss_metadata.pkl")
        
        try:
            # 创建第一个实例并添加数据
            store1 = FaissStore()
            test_points = [
                {
                    'file_path': 'test1.py',
                    'content': 'def hello():\n    print("Hello, world!")',
                    'embedding': [0.1] * settings.embedding_dim,
                    'start_line': 1,
                    'end_line': 2,
                    'chunk_size': 20,
                },
            ]
            store1.add_points(test_points)
            assert store1.get_index_size() == 1
            
            # 创建第二个实例，应该加载已保存的索引
            store2 = FaissStore()
            assert store2.get_index_size() == 1
            assert len(store2.metadata) == 1
            assert store2.metadata[0]['file_path'] == 'test1.py'
            
        finally:
            # 恢复原始配置
            settings.faiss_index_path = original_index_path
            settings.faiss_metadata_path = original_metadata_path


if __name__ == "__main__":
    pytest.main(["-v", __file__])
