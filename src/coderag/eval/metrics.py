from typing import List, Dict, Any


class EvaluationMetrics:
    """评测指标计算"""

    @staticmethod
    def recall_at_k(relevant_docs: List[str], retrieved_docs: List[Dict[str, Any]], k: int) -> float:
        """计算Recall@k"""
        if not relevant_docs:
            return 1.0
        retrieved_file_paths = [doc['file_path'] for doc in retrieved_docs[:k]]
        relevant_retrieved = set(relevant_docs) & set(retrieved_file_paths)
        return len(relevant_retrieved) / len(relevant_docs)

    @staticmethod
    def mrr(relevant_docs: List[str], retrieved_docs: List[Dict[str, Any]]) -> float:
        """计算MRR（Mean Reciprocal Rank）"""
        for i, doc in enumerate(retrieved_docs):
            if doc['file_path'] in relevant_docs:
                return 1.0 / (i + 1)
        return 0.0

    @staticmethod
    def accuracy(predicted_answers: List[str], ground_truths: List[str]) -> float:
        """计算正确率"""
        if not predicted_answers:
            return 0.0
        correct = 0
        for pred, gt in zip(predicted_answers, ground_truths):
            if EvaluationMetrics._is_correct(pred, gt):
                correct += 1
        return correct / len(predicted_answers)

    @staticmethod
    def no_reference_rate(answers: List[Dict[str, Any]]) -> float:
        """计算无引用率"""
        if not answers:
            return 0.0
        no_reference_count = 0
        for answer in answers:
            if not answer.get('references'):
                no_reference_count += 1
        return no_reference_count / len(answers)

    @staticmethod
    def _is_correct(predicted: str, ground_truth: str) -> bool:
        """判断回答是否正确（简单实现）"""
        # 这里可以根据实际需求实现更复杂的判断逻辑
        predicted_lower = predicted.lower()
        ground_truth_lower = ground_truth.lower()
        return ground_truth_lower in predicted_lower