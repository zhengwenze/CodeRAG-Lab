from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, CollectionDescription
from coderag.settings import settings


class QdrantStore:
    """Qdrant向量存储"""

    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        self.collection_name = settings.qdrant_collection
        self.embedding_dim = settings.embedding_dim

    def create_collection(self):
        """创建集合"""
        try:
            # 检查集合是否存在
            collections = self.client.get_collections()
            collection_exists = any(
                col.name == self.collection_name
                for col in collections.collections
            )

            if not collection_exists:
                # 创建集合
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config={
                        "size": self.embedding_dim,
                        "distance": "Cosine",
                    },
                )
                print(f"Collection {self.collection_name} created successfully")
            else:
                print(f"Collection {self.collection_name} already exists")
        except Exception as e:
            print(f"Error creating collection: {e}")

    def add_points(self, points: List[Dict[str, Any]]):
        """添加向量点"""
        try:
            point_structs = []
            for i, point in enumerate(points):
                point_id = i
                vector = point['embedding']
                payload = {
                    'file_path': point['file_path'],
                    'start_line': point.get('start_line'),
                    'end_line': point.get('end_line'),
                    'content': point['content'],
                    'chunk_size': point.get('chunk_size'),
                    'structure_type': point.get('structure_type'),
                    'structure_name': point.get('structure_name'),
                }
                point_struct = PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
                point_structs.append(point_struct)

            # 批量添加
            self.client.upsert(
                collection_name=self.collection_name,
                points=point_structs,
            )
            print(f"Added {len(point_structs)} points to collection")
        except Exception as e:
            print(f"Error adding points: {e}")

    def search(self, query_vector: List[float], top_k: int = 5):
        """搜索相似向量"""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                with_payload=True,
                with_vectors=False,
            )

            search_results = []
            for i, result in enumerate(results):
                search_results.append({
                    'file_path': result.payload.get('file_path'),
                    'start_line': result.payload.get('start_line'),
                    'end_line': result.payload.get('end_line'),
                    'content': result.payload.get('content'),
                    'score': result.score,
                    'rank': i + 1,
                })

            return search_results
        except Exception as e:
            print(f"Error searching: {e}")
            return []

    def delete_collection(self):
        """删除集合"""
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            print(f"Collection {self.collection_name} deleted successfully")
        except Exception as e:
            print(f"Error deleting collection: {e}")