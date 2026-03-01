import json
from typing import List, Dict, Any, Optional
from pathlib import Path


class EvaluationDataset:
    """评测数据集"""

    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.dataset_name = ""
        self.repo_name = ""
        self.data = self.load_dataset()

    def load_dataset(self) -> List[Dict[str, Any]]:
        """加载评测数据集"""
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                self.dataset_name = "coderag_eval_v1"
                self.repo_name = "unknown"
                return data
            
            self.dataset_name = data.get('dataset_name', 'unknown')
            self.repo_name = data.get('repo_name', 'unknown')
            return data.get('items', [])
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return []

    def get_questions(self) -> List[str]:
        """获取所有问题"""
        return [item['question'] for item in self.data]

    def get_gold(self, question_id: str) -> Dict[str, Any]:
        """获取问题的黄金答案"""
        for item in self.data:
            if item.get('id') == question_id:
                return item.get('gold', {})
        return {}

    def get_question_by_id(self, question_id: str) -> Optional[str]:
        """根据ID获取问题"""
        for item in self.data:
            if item.get('id') == question_id:
                return item.get('question')
        return None

    def get_must_cite_sources(self, question_id: str) -> List[str]:
        """获取必须引用的来源"""
        gold = self.get_gold(question_id)
        return gold.get('must_cite_sources', [])

    def get_answer_must_contain(self, question_id: str) -> List[str]:
        """获取回答必须包含的关键词"""
        gold = self.get_gold(question_id)
        return gold.get('answer_must_contain', [])

    def get_tags(self, question_id: str) -> List[str]:
        """获取问题标签"""
        for item in self.data:
            if item.get('id') == question_id:
                return item.get('tags', [])
        return []

    def get_all_tags(self) -> List[str]:
        """获取所有标签"""
        tags = set()
        for item in self.data:
            tags.update(item.get('tags', []))
        return sorted(list(tags))

    def get_questions_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """根据标签获取问题"""
        return [item for item in self.data if tag in item.get('tags', [])]

    def __len__(self) -> int:
        """返回数据集大小"""
        return len(self.data)
