import re
from typing import List, Dict, Any, Optional
from collections import defaultdict


class EvaluationMetrics:
    """评测指标计算"""

    @staticmethod
    def hit_rate_at_k(relevant_sources: List[str], retrieved_docs: List[Dict[str, Any]], k: int) -> float:
        """计算Hit Rate@k - top-k 是否包含 gold source"""
        if not relevant_sources:
            return 1.0
        
        retrieved_file_paths = []
        for doc in retrieved_docs[:k]:
            file_path = doc.get('file_path', '')
            retrieved_file_paths.append(file_path)
        
        relevant_retrieved = set(relevant_sources) & set(retrieved_file_paths)
        return 1.0 if relevant_retrieved else 0.0

    @staticmethod
    def recall_at_k(relevant_sources: List[str], retrieved_docs: List[Dict[str, Any]], k: int) -> float:
        """计算Recall@k - 召回率"""
        if not relevant_sources:
            return 1.0
        
        retrieved_file_paths = [doc.get('file_path', '') for doc in retrieved_docs[:k]]
        relevant_retrieved = set(relevant_sources) & set(retrieved_file_paths)
        return len(relevant_retrieved) / len(relevant_sources)

    @staticmethod
    def mrr(relevant_sources: List[str], retrieved_docs: List[Dict[str, Any]]) -> float:
        """计算MRR（Mean Reciprocal Rank）"""
        for i, doc in enumerate(retrieved_docs):
            if doc.get('file_path', '') in relevant_sources:
                return 1.0 / (i + 1)
        return 0.0

    @staticmethod
    def citation_rate(answer: str) -> float:
        """计算Citation Rate - 回答是否包含 [SOURCE n] 引用"""
        if not answer:
            return 0.0
        
        citation_pattern = r'\[SOURCE\s+\d+\]'
        matches = re.findall(citation_pattern, answer, re.IGNORECASE)
        return 1.0 if matches else 0.0

    @staticmethod
    def contains_rate(answer: str, required_keywords: List[str]) -> float:
        """计算Contains Rate - 是否包含所有必需关键词"""
        if not answer or not required_keywords:
            return 0.0 if required_keywords else 1.0
        
        answer_lower = answer.lower()
        matched_count = sum(1 for keyword in required_keywords if keyword.lower() in answer_lower)
        return matched_count / len(required_keywords)

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
        predicted_lower = predicted.lower()
        ground_truth_lower = ground_truth.lower()
        return ground_truth_lower in predicted_lower

    @staticmethod
    def compute_all_metrics(
        question_id: str,
        question: str,
        answer: str,
        retrieved_docs: List[Dict[str, Any]],
        must_cite_sources: List[str],
        answer_must_contain: List[str],
        k: int = 5
    ) -> Dict[str, Any]:
        """计算单个问题的所有评测指标"""
        
        hit_rate = EvaluationMetrics.hit_rate_at_k(must_cite_sources, retrieved_docs, k)
        recall = EvaluationMetrics.recall_at_k(must_cite_sources, retrieved_docs, k)
        mrr = EvaluationMetrics.mrr(must_cite_sources, retrieved_docs)
        citation_rate = EvaluationMetrics.citation_rate(answer)
        contains_rate = EvaluationMetrics.contains_rate(answer, answer_must_contain)
        
        return {
            'question_id': question_id,
            'question': question,
            'answer': answer,
            'retrieved_docs_count': len(retrieved_docs),
            'hit_rate_at_k': hit_rate,
            'recall_at_k': recall,
            'mrr': mrr,
            'citation_rate': citation_rate,
            'contains_rate': contains_rate,
            'must_cite_sources': must_cite_sources,
            'retrieved_sources': [doc.get('file_path', '') for doc in retrieved_docs[:k]],
            'answer_must_contain': answer_must_contain,
        }

    @staticmethod
    def aggregate_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """聚合多个问题的评测结果"""
        if not results:
            return {}
        
        total = len(results)
        
        hit_rates = [r['hit_rate_at_k'] for r in results]
        recalls = [r['recall_at_k'] for r in results]
        mrrs = [r['mrr'] for r in results]
        citation_rates = [r['citation_rate'] for r in results]
        contains_rates = [r['contains_rate'] for r in results]
        
        return {
            'total_questions': total,
            'hit_rate_at_k': sum(hit_rates) / total,
            'recall_at_k': sum(recalls) / total,
            'mrr': sum(mrrs) / total,
            'citation_rate': sum(citation_rates) / total,
            'contains_rate': sum(contains_rates) / total,
            'hit_count': sum(1 for h in hit_rates if h > 0),
            'citation_count': sum(1 for c in citation_rates if c > 0),
            'contains_count': sum(1 for c in contains_rates if c >= 0.5),
        }

    @staticmethod
    def aggregate_by_tag(results: List[Dict[str, Any]], tags_map: Dict[str, List[str]]) -> Dict[str, Dict[str, float]]:
        """按标签聚合评测结果"""
        tag_results = defaultdict(list)
        
        for result in results:
            question_id = result.get('question_id', '')
            tags = tags_map.get(question_id, [])
            for tag in tags:
                tag_results[tag].append(result)
        
        tag_metrics = {}
        for tag, tag_items in tag_results.items():
            aggregated = EvaluationMetrics.aggregate_metrics(tag_items)
            tag_metrics[tag] = aggregated
        
        return tag_metrics
