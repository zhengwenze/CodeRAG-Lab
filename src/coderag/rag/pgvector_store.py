from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class PgVectorStore:
    """PostgreSQL + pgvector 向量存储"""
    
    def __init__(
        self,
        connection_string: str = "postgresql://user:password@localhost:5432/coderag",
        collection_name: str = "coderag",
        dimension: int = 384,
    ):
        self.connection_string = connection_string
        self.collection_name = collection_name
        self.dimension = dimension
        self._conn = None
        self._cursor = None
    
    def connect(self) -> None:
        """建立数据库连接"""
        try:
            import psycopg2
            from pgvector.psycopg2 import register_vector
            
            self._conn = psycopg2.connect(self.connection_string)
            self._conn.autocommit = True
            self._cursor = self._conn.cursor()
            register_vector(self._conn)
            
            self._ensure_table()
            logger.info(f"已连接到 PostgreSQL: {self.collection_name}")
        except ImportError:
            logger.error("请安装 psycopg2 和 pgvector: pip install psycopg2-binary pgvector")
            raise
    
    def _ensure_table(self) -> None:
        """确保表和索引存在"""
        self._cursor.execute(f"CREATE EXTENSION IF NOT EXISTS vector")
        
        self._cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.collection_name} (
                id SERIAL PRIMARY KEY,
                chunk_id VARCHAR(255) UNIQUE NOT NULL,
                document_id VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                embedding vector({self.dimension}),
                search_vector tsvector,
                metadata JSONB,
                create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self._cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{self.collection_name}_embedding 
            ON {self.collection_name} USING hnsw (embedding vector_cosine_ops)
        """)
        
        self._cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{self.collection_name}_search 
            ON {self.collection_name} USING gin (search_vector)
        """)
        
        self._cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{self.collection_name}_document 
            ON {self.collection_name} (document_id)
        """)

    def add_texts(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """添加文本和向量"""
        if self._conn is None:
            self.connect()
        
        if ids is None:
            ids = [f"chunk_{i}_{hash(text)}" for i, text in enumerate(texts)]
        
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        for i, (text, embedding, metadata, chunk_id) in enumerate(
            zip(texts, embeddings, metadatas, ids)
        ):
            search_vector = self._text_to_tsvector(text)
            
            self._cursor.execute(
                f"""
                INSERT INTO {self.collection_name} 
                (chunk_id, document_id, content, embedding, search_vector, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (chunk_id) DO UPDATE SET
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    search_vector = EXCLUDED.search_vector,
                    metadata = EXCLUDED.metadata
                """,
                (
                    chunk_id,
                    metadata.get("document_id", ""),
                    text,
                    embedding,
                    json.dumps(metadata),
                )
            )
        
        return ids

    def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """向量相似度检索"""
        if self._conn is None:
            self.connect()
        
        query = f"""
            SELECT chunk_id, document_id, content, metadata,
                   1 - (embedding <=> %s::vector) as similarity
            FROM {self.collection_name}
            WHERE 1=1
        """
        params = [query_embedding]
        
        if filter:
            for key, value in filter.items():
                query += f" AND metadata->>%s = %s"
                params.extend([key, str(value)])
        
        query += f" ORDER BY embedding <=> %s::vector LIMIT {k}"
        params.append(query_embedding)
        
        self._cursor.execute(query, params)
        results = self._cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "document_id": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]) if row[3] else {},
                "score": float(row[4]),
            }
            for row in results
        ]

    def fulltext_search(
        self,
        query: str,
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        """全文检索"""
        if self._conn is None:
            self.connect()
        
        ts_query = self._text_to_tsquery(query)
        
        self._cursor.execute(
            f"""
            SELECT chunk_id, document_id, content, metadata,
                   ts_rank_cd(search_vector, websearch_to_tsquery('simple', %s)) as rank
            FROM {self.collection_name}
            WHERE search_vector @@ websearch_to_tsquery('simple', %s)
            ORDER BY rank DESC
            LIMIT {k}
            """,
            [query, query]
        )
        
        results = self._cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "document_id": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]) if row[3] else {},
                "score": float(row[4]),
            }
            for row in results
        ]

    def hybrid_search(
        self,
        query: str,
        query_embedding: List[float],
        k: int = 5,
        vector_weight: float = 0.5,
        fulltext_weight: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """混合检索"""
        if self._conn is None:
            self.connect()
        
        ts_query = self._text_to_tsquery(query)
        
        self._cursor.execute(
            f"""
            SELECT chunk_id, document_id, content, metadata,
                   COALESCE(1 - (embedding <=> %s::vector), 0) * {vector_weight} +
                   COALESCE(ts_rank_cd(search_vector, websearch_to_tsquery('simple', %s)), 0) * {fulltext_weight} as score
            FROM {self.collection_name}
            WHERE embedding IS NOT NULL OR search_vector IS NOT NULL
            ORDER BY score DESC
            LIMIT {k}
            """,
            [query_embedding, query]
        )
        
        results = self._cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "document_id": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]) if row[3] else {},
                "score": float(row[4]),
            }
            for row in results
        ]

    def delete_by_document_id(self, document_id: str) -> None:
        """根据文档ID删除"""
        if self._conn is None:
            self.connect()
        
        self._cursor.execute(
            f"DELETE FROM {self.collection_name} WHERE document_id = %s",
            [document_id]
        )

    def delete_collection(self) -> None:
        """删除整个集合"""
        if self._conn is None:
            self.connect()
        
        self._cursor.execute(f"DROP TABLE IF EXISTS {self.collection_name}")
        logger.info(f"已删除集合: {self.collection_name}")

    def close(self) -> None:
        """关闭连接"""
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()
        logger.info("已关闭 PostgreSQL 连接")

    @staticmethod
    def _text_to_tsvector(text: str) -> str:
        """文本转 tsvector"""
        import re
        words = re.findall(r'\w+', text.lower())
        return ' '.join(words)

    @staticmethod
    def _text_to_tsquery(query: str) -> str:
        """文本转 tsquery"""
        import re
        words = re.findall(r'\w+', query.lower())
        return ' & '.join(words)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
