import json
import os
from datetime import datetime
from typing import Dict, Any, List
from coderag.settings import settings
from coderag.eval.dataset import EvaluationDataset
from coderag.eval.metrics import EvaluationMetrics
from coderag.llm.provider import LLMProviderFactory
from coderag.llm.lora import get_lora_provider
from coderag.rag.retriever import Retriever
from coderag.rag.prompt import PromptTemplate


class LoRAComparisonRunner:
    """LoRA微调与原始模型对比评测运行器"""

    def __init__(self, dataset_path: str = None, top_k: int = None, lora_model_path: str = None):
        self.dataset_path = dataset_path or settings.eval_dataset_path
        self.top_k = top_k or settings.top_k
        self.lora_model_path = lora_model_path
        self.dataset = EvaluationDataset(self.dataset_path)
        self.original_llm = LLMProviderFactory.get_provider(settings.llm_provider)
        self.lora_provider = None
        if lora_model_path:
            self.lora_provider = get_lora_provider(lora_model_path)
        self.retriever = Retriever()

    def run_comparison(self) -> Dict[str, Any]:
        """运行对比评测"""
        print(f"\n{'='*80}")
        print("LoRA FINE-TUNING COMPARISON EVALUATION")
        print(f"{'='*80}\n")

        results = {
            'dataset_name': self.dataset.dataset_name,
            'repo_name': self.dataset.repo_name,
            'total_questions': len(self.dataset),
            'top_k': self.top_k,
            'timestamp': datetime.utcnow().isoformat(),
            'lora_model_path': self.lora_model_path,
            'original_model': settings.llm_provider,
            'questions': [],
            'metrics': {
                'original': {},
                'lora': {},
                'diff': {}
            },
            'tag_metrics': {
                'original': {},
                'lora': {}
            },
        }

        question_results = {
            'original': [],
            'lora': []
        }
        tags_map = {}

        for item in self.dataset.data:
            question_id = item.get('id', 'unknown')
            question = item.get('question', '')
            gold = item.get('gold', {})
            must_cite_sources = gold.get('must_cite_sources', [])
            answer_must_contain = gold.get('answer_must_contain', [])
            tags = item.get('tags', [])
            
            tags_map[question_id] = tags

            print(f"Processing: {question_id} - {question[:50]}...")

            # 1. 原始模型评测
            print("  - Original model...")
            original_result = self._evaluate_model(
                self.original_llm,
                question,
                must_cite_sources,
                answer_must_contain
            )
            question_results['original'].append(original_result)

            # 2. LoRA微调模型评测
            if self.lora_provider:
                print("  - LoRA fine-tuned model...")
                lora_result = self._evaluate_model(
                    self.lora_provider,
                    question,
                    must_cite_sources,
                    answer_must_contain
                )
                question_results['lora'].append(lora_result)

            # 3. 保存问题级结果
            question_data = {
                'question_id': question_id,
                'question': question,
                'original': {
                    'answer': original_result.get('answer', ''),
                    'retrieved_sources': original_result.get('retrieved_sources', []),
                    'hit_rate_at_k': original_result.get('hit_rate_at_k', 0),
                    'recall_at_k': original_result.get('recall_at_k', 0),
                    'mrr': original_result.get('mrr', 0),
                    'citation_rate': original_result.get('citation_rate', 0),
                    'contains_rate': original_result.get('contains_rate', 0),
                }
            }

            if self.lora_provider:
                question_data['lora'] = {
                    'answer': lora_result.get('answer', ''),
                    'retrieved_sources': lora_result.get('retrieved_sources', []),
                    'hit_rate_at_k': lora_result.get('hit_rate_at_k', 0),
                    'recall_at_k': lora_result.get('recall_at_k', 0),
                    'mrr': lora_result.get('mrr', 0),
                    'citation_rate': lora_result.get('citation_rate', 0),
                    'contains_rate': lora_result.get('contains_rate', 0),
                }

            results['questions'].append(question_data)

        # 4. 聚合评测结果
        original_aggregated = EvaluationMetrics.aggregate_metrics(question_results['original'])
        results['metrics']['original'] = original_aggregated

        if self.lora_provider:
            lora_aggregated = EvaluationMetrics.aggregate_metrics(question_results['lora'])
            results['metrics']['lora'] = lora_aggregated
            
            # 计算差异
            diff = self._compute_diff(original_aggregated, lora_aggregated)
            results['metrics']['diff'] = diff

        # 5. 按标签聚合
        original_tag_metrics = EvaluationMetrics.aggregate_by_tag(question_results['original'], tags_map)
        results['tag_metrics']['original'] = original_tag_metrics

        if self.lora_provider:
            lora_tag_metrics = EvaluationMetrics.aggregate_by_tag(question_results['lora'], tags_map)
            results['tag_metrics']['lora'] = lora_tag_metrics

        # 6. 保存结果
        self.save_results(results)
        
        # 7. 打印摘要
        self.print_summary(results)

        return results

    def _evaluate_model(self, llm, question: str, must_cite_sources: List[str], answer_must_contain: List[str]) -> Dict[str, Any]:
        """使用指定模型评测单个问题"""
        # 检索相关文档
        embedding = llm.embed(question)
        retrieved_docs = self.retriever.retrieve(question, embedding, self.top_k)

        # 生成回答
        contexts = [
            {
                'file_path': doc.get('file_path', ''),
                'content': doc.get('content', ''),
                'start_line': doc.get('start_line'),
                'end_line': doc.get('end_line'),
            }
            for doc in retrieved_docs
        ]
        prompt = PromptTemplate.rag_prompt(question, contexts)
        answer = llm.generate(prompt)

        # 计算评测指标
        metrics_result = EvaluationMetrics.compute_all_metrics(
            question_id='temp',
            question=question,
            answer=answer,
            retrieved_docs=retrieved_docs,
            must_cite_sources=must_cite_sources,
            answer_must_contain=answer_must_contain,
            k=self.top_k
        )
        
        metrics_result['answer'] = answer
        return metrics_result

    def _compute_diff(self, original: Dict[str, Any], lora: Dict[str, Any]) -> Dict[str, Any]:
        """计算原始模型与LoRA模型的指标差异"""
        diff = {}
        for metric in original:
            if isinstance(original[metric], (int, float)) and metric in lora:
                diff[metric] = lora[metric] - original[metric]
        return diff

    def save_results(self, results: Dict[str, Any]):
        """保存评测结果"""
        output_dir = os.path.join(settings.eval_output_path, 'lora_comparison')
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        dataset_name = results.get('dataset_name', 'eval')
        output_file = os.path.join(output_dir, f"{dataset_name}_lora_comparison_{timestamp}.json")

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\nComparison results saved to: {output_file}")
            self.latest_result_file = output_file
        except Exception as e:
            print(f"Error saving results: {e}")

    def print_summary(self, results: Dict[str, Any]):
        """打印评测摘要"""
        print(f"\n{'='*80}")
        print("LORA COMPARISON SUMMARY")
        print(f"{'='*80}")
        print(f"Dataset: {results.get('dataset_name', 'unknown')}")
        print(f"Total Questions: {results.get('total_questions', 0)}")
        print(f"Original Model: {results.get('original_model', 'unknown')}")
        print(f"LoRA Model: {os.path.basename(results.get('lora_model_path', 'unknown'))}")
        print(f"{'='*80}\n")

        # 打印原始模型指标
        original_metrics = results.get('metrics', {}).get('original', {})
        print("ORIGINAL MODEL METRICS:")
        print(f"  Hit Rate@{self.top_k}: {original_metrics.get('hit_rate_at_k', 0):.4f}")
        print(f"  Recall@{self.top_k}:    {original_metrics.get('recall_at_k', 0):.4f}")
        print(f"  MRR:                {original_metrics.get('mrr', 0):.4f}")
        print(f"  Citation Rate:     {original_metrics.get('citation_rate', 0):.4f}")
        print(f"  Contains Rate:      {original_metrics.get('contains_rate', 0):.4f}")

        # 打印LoRA模型指标
        lora_metrics = results.get('metrics', {}).get('lora', {})
        if lora_metrics:
            print("\nLORA FINE-TUNED MODEL METRICS:")
            print(f"  Hit Rate@{self.top_k}: {lora_metrics.get('hit_rate_at_k', 0):.4f}")
            print(f"  Recall@{self.top_k}:    {lora_metrics.get('recall_at_k', 0):.4f}")
            print(f"  MRR:                {lora_metrics.get('mrr', 0):.4f}")
            print(f"  Citation Rate:     {lora_metrics.get('citation_rate', 0):.4f}")
            print(f"  Contains Rate:      {lora_metrics.get('contains_rate', 0):.4f}")

            # 打印差异
            diff = results.get('metrics', {}).get('diff', {})
            print("\nPERFORMANCE DIFF (LoRA - Original):")
            print(f"  Hit Rate@{self.top_k}: {diff.get('hit_rate_at_k', 0):+.4f}")
            print(f"  Recall@{self.top_k}:    {diff.get('recall_at_k', 0):+.4f}")
            print(f"  MRR:                {diff.get('mrr', 0):+.4f}")
            print(f"  Citation Rate:     {diff.get('citation_rate', 0):+.4f}")
            print(f"  Contains Rate:      {diff.get('contains_rate', 0):+.4f}")

        print(f"\n{'='*80}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CodeRAG LoRA Comparison Runner")
    parser.add_argument('--dataset', type=str, default=None, help="Dataset path")
    parser.add_argument('--top-k', type=int, default=None, help="Top-k for retrieval")
    parser.add_argument('--lora-model', type=str, required=True, help="Path to LoRA fine-tuned model")
    
    args = parser.parse_args()
    
    runner = LoRAComparisonRunner(
        dataset_path=args.dataset,
        top_k=args.top_k,
        lora_model_path=args.lora_model
    )
    
    runner.run_comparison()
