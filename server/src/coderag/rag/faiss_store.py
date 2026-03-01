from typing import List, Dict, Any
import faiss
import os
import pickle
from coderag.settings import settings


class FaissStore:
    """FAISS向量存储"""

    def __init__(self):
        self.index_path = settings.faiss_index_path
        self.metadata_path = settings.faiss_metadata_path
        self.embedding_dim = settings.embedding_dim
        self.index = None
        self.metadata = []
        self._load_index()

    def _load_index(self):
        """加载FAISS索引"""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                # 加载索引
                self.index = faiss.read_index(self.index_path)
                # 加载元数据
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                print(f"FAISS index loaded successfully with {len(self.metadata)} points")
            else:
                # 创建新索引
                self._create_index()
        except Exception as e:
            print(f"Error loading FAISS index: {e}")
            self._create_index()

    def _create_index(self):
        """创建FAISS索引"""
        try:
            # 创建Flat索引（余弦相似度）
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            # 归一化向量以使用点积作为余弦相似度
            self.metadata = []
            print(f"FAISS index created successfully with dimension {self.embedding_dim}")
        except Exception as e:
            print(f"Error creating FAISS index: {e}")

    def _save_index(self):
        """保存FAISS索引"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            # 保存索引
            faiss.write_index(self.index, self.index_path)
            # 保存元数据
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            print(f"FAISS index saved successfully")
        except Exception as e:
            print(f"Error saving FAISS index: {e}")

    def add_points(self, points: List[Dict[str, Any]]):
        """添加向量点"""
        try:
            # 提取向量和元数据
            vectors = []
            new_metadata = []
            
            for point in points:
                vector = point['embedding']
                # 归一化向量
                norm = sum(v*v for v in vector)**0.5
                normalized_vector = [v/norm for v in vector]
                vectors.append(normalized_vector)
                
                # 保存元数据
                metadata = {
                    'file_path': point['file_path'],
                    'start_line': point.get('start_line'),
                    'end_line': point.get('end_line'),
                    'content': point['content'],
                    'chunk_size': point.get('chunk_size'),
                }
                new_metadata.append(metadata)
            
            # 转换为numpy数组
            import numpy as np
            vectors = np.array(vectors, dtype=np.float32)
            
            # 添加到索引
            self.index.add(vectors)
            self.metadata.extend(new_metadata)
            
            # 保存索引
            self._save_index()
            
            print(f"Added {len(points)} points to FAISS index")
        except Exception as e:
            print(f"Error adding points to FAISS index: {e}")

    def search(self, query_vector: List[float], top_k: int = 5):
        """搜索相似向量"""
        try:
            # 归一化查询向量
            norm = sum(v*v for v in query_vector)**0.5
            normalized_query = [v/norm for v in query_vector]
            
            # 转换为numpy数组
            import numpy as np
            query = np.array([normalized_query], dtype=np.float32)
            
            # 搜索
            distances, indices = self.index.search(query, top_k)
            
            search_results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.metadata):
                    metadata = self.metadata[idx]
                    search_results.append({
                        'file_path': metadata['file_path'],
                        'start_line': metadata.get('start_line'),
                        'end_line': metadata.get('end_line'),
                        'content': metadata['content'],
                        'score': float(dist),  # 点积结果
                        'rank': i + 1,
                    })
            
            return search_results
        except Exception as e:
            print(f"Error searching FAISS index: {e}")
            return []

    def clear_index(self):
        """清空索引"""
        try:
            self._create_index()
            self._save_index()
            print("FAISS index cleared successfully")
        except Exception as e:
            print(f"Error clearing FAISS index: {e}")

    def get_index_size(self):
        """获取索引大小"""
        if self.index:
            return self.index.ntotal
        return 0
