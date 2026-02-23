import json
from typing import List, Dict, Any


class EvaluationDataset:
    """评测数据集"""

    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.data = self.load_dataset()

    def load_dataset(self) -> List[Dict[str, Any]]:
        """加载评测数据集"""
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return []

    def get_questions(self) -> List[str]:
        """获取所有问题"""
        return [item['question'] for item in self.data]

    def get_ground_truth(self, question: str) -> Dict[str, Any]:
        """获取问题的标准答案"""
        for item in self.data:
            if item['question'] == question:
                return item.get('ground_truth', {})
        return {}

    def get_relevant_docs(self, question: str) -> List[str]:
        """获取问题的相关文档"""
        for item in self.data:
            if item['question'] == question:
                return item.get('relevant_docs', [])
        return []

    def __len__(self) -> int:
        """返回数据集大小"""
        return len(self.data)