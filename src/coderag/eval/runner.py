import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from coderag.settings import settings
from coderag.eval.dataset import EvaluationDataset
from coderag.eval.metrics import EvaluationMetrics
from coderag.llm.provider import LLMProviderFactory
from coderag.rag.retriever import Retriever
from coderag.rag.prompt import PromptTemplate


class EvaluationRunner:
    """评测运行器"""

    def __init__(self, dataset_path: str = None, top_k: int = None, skip_llm: bool = False):
        self.dataset_path = dataset_path or settings.eval_dataset_path
        self.top_k = top_k or settings.top_k
        self.skip_llm = skip_llm
        self.dataset = EvaluationDataset(self.dataset_path)
        self.llm = LLMProviderFactory.get_provider(settings.llm_provider)
        self.retriever = Retriever()

    def run_evaluation(self) -> Dict[str, Any]:
        """运行完整评测"""
        print(f"\n{'='*60}")
        print(f"Running evaluation on dataset: {self.dataset.dataset_name}")
        print(f"Dataset path: {self.dataset_path}")
        print(f"Top-k: {self.top_k}")
        print(f"Skip LLM: {self.skip_llm}")
        print(f"{'='*60}\n")

        results = {
            'dataset_name': self.dataset.dataset_name,
            'repo_name': self.dataset.repo_name,
            'total_questions': len(self.dataset),
            'top_k': self.top_k,
            'timestamp': datetime.utcnow().isoformat(),
            'questions': [],
            'metrics': {},
            'tag_metrics': {},
        }

        question_results = []
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

            embedding = self.llm.embed(question)
            retrieved_docs = self.retriever.retrieve(question, embedding, self.top_k)

            if self.skip_llm:
                answer = ""
            else:
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
                answer = self.llm.generate(prompt)

            metrics_result = EvaluationMetrics.compute_all_metrics(
                question_id=question_id,
                question=question,
                answer=answer,
                retrieved_docs=retrieved_docs,
                must_cite_sources=must_cite_sources,
                answer_must_contain=answer_must_contain,
                k=self.top_k
            )

            question_results.append(metrics_result)

            results['questions'].append({
                'question_id': question_id,
                'question': question,
                'answer': answer if answer else None,
                'retrieved_sources': metrics_result['retrieved_sources'],
                'hit_rate_at_k': metrics_result['hit_rate_at_k'],
                'recall_at_k': metrics_result['recall_at_k'],
                'mrr': metrics_result['mrr'],
                'citation_rate': metrics_result['citation_rate'],
                'contains_rate': metrics_result['contains_rate'],
            })

        aggregated = EvaluationMetrics.aggregate_metrics(question_results)
        results['metrics'] = aggregated

        tag_metrics = EvaluationMetrics.aggregate_by_tag(question_results, tags_map)
        results['tag_metrics'] = tag_metrics

        self.save_results(results)
        self.print_summary(aggregated, tag_metrics)

        return results

    def print_summary(self, aggregated: Dict[str, Any], tag_metrics: Dict[str, Any]):
        """打印评测摘要"""
        print(f"\n{'='*60}")
        print("EVALUATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total Questions: {aggregated.get('total_questions', 0)}")
        print(f"\nCore Metrics:")
        print(f"  Hit Rate@{self.top_k}: {aggregated.get('hit_rate_at_k', 0):.4f} ({aggregated.get('hit_count', 0)}/{aggregated.get('total_questions', 0)})")
        print(f"  Recall@{self.top_k}:    {aggregated.get('recall_at_k', 0):.4f}")
        print(f"  MRR:                {aggregated.get('mrr', 0):.4f}")
        print(f"  Citation Rate:     {aggregated.get('citation_rate', 0):.4f} ({aggregated.get('citation_count', 0)}/{aggregated.get('total_questions', 0)})")
        print(f"  Contains Rate:      {aggregated.get('contains_rate', 0):.4f} ({aggregated.get('contains_count', 0)}/{aggregated.get('total_questions', 0)})")
        
        if tag_metrics:
            print(f"\nMetrics by Tag:")
            for tag, tag_metric in tag_metrics.items():
                print(f"  [{tag}] hit_rate: {tag_metric.get('hit_rate_at_k', 0):.4f}, citation: {tag_metric.get('citation_rate', 0):.4f}")
        
        print(f"{'='*60}\n")

    def save_results(self, results: Dict[str, Any]):
        """保存评测结果"""
        output_dir = settings.eval_output_path
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        dataset_name = results.get('dataset_name', 'eval')
        output_file = os.path.join(output_dir, f"{dataset_name}_{timestamp}.json")

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Evaluation results saved to: {output_file}")
            self.latest_result_file = output_file
        except Exception as e:
            print(f"Error saving results: {e}")

    def compare_with_previous(self, previous_file: Optional[str] = None) -> Dict[str, Any]:
        """与之前的评测结果进行对比（回归测试）"""
        if previous_file is None:
            previous_file = self._find_latest_result()
        
        if not previous_file or not os.path.exists(previous_file):
            print("No previous results found for comparison")
            return {}
        
        with open(previous_file, 'r', encoding='utf-8') as f:
            previous = json.load(f)
        
        current = self._get_current_results()
        
        comparison = self._compute_diff(previous, current)
        
        print(f"\n{'='*60}")
        print("REGRESSION TEST COMPARISON")
        print(f"{'='*60}")
        print(f"Previous: {previous.get('timestamp', 'unknown')}")
        print(f"Current:  {current.get('timestamp', 'unknown')}")
        print(f"\nMetrics Change:")
        for metric, diff in comparison.get('metrics_diff', {}).items():
            sign = "+" if diff > 0 else ""
            print(f"  {metric}: {sign}{diff:.4f}")
        
        if comparison.get('regressions'):
            print(f"\nRegressions detected:")
            for reg in comparison['regressions']:
                print(f"  - {reg}")
        
        print(f"{'='*60}\n")
        
        return comparison

    def _find_latest_result(self) -> Optional[str]:
        """查找最新的评测结果文件"""
        output_dir = settings.eval_output_path
        if not os.path.exists(output_dir):
            return None
        
        result_files = []
        for f in os.listdir(output_dir):
            if f.endswith('.json') and f.startswith(self.dataset.dataset_name):
                file_path = os.path.join(output_dir, f)
                result_files.append((file_path, os.path.getmtime(file_path)))
        
        if not result_files:
            return None
        
        result_files.sort(key=lambda x: x[1], reverse=True)
        return result_files[0][0]

    def _compute_diff(self, previous: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        """计算两次评测结果的差异"""
        prev_metrics = previous.get('metrics', {})
        curr_metrics = current.get('metrics', {})
        
        metrics_diff = {}
        for key in curr_metrics:
            if isinstance(curr_metrics[key], (int, float)):
                prev_val = prev_metrics.get(key, 0)
                curr_val = curr_metrics[key]
                metrics_diff[key] = curr_val - prev_val
        
        regressions = []
        if metrics_diff.get('hit_rate_at_k', 0) < 0:
            regressions.append(f"Hit Rate dropped by {-metrics_diff['hit_rate_at_k']:.4f}")
        if metrics_diff.get('citation_rate', 0) < 0:
            regressions.append(f"Citation Rate dropped by {-metrics_diff['citation_rate']:.4f}")
        
        return {
            'previous_timestamp': previous.get('timestamp'),
            'current_timestamp': current.get('timestamp'),
            'metrics_diff': metrics_diff,
            'regressions': regressions,
        }

    def _get_current_results(self) -> Dict[str, Any]:
        """获取当前评测结果（不重新运行）"""
        results = {
            'dataset_name': self.dataset.dataset_name,
            'repo_name': self.dataset.repo_name,
            'total_questions': len(self.dataset),
            'top_k': self.top_k,
            'timestamp': datetime.utcnow().isoformat(),
            'questions': [],
            'metrics': {},
            'tag_metrics': {},
        }

        question_results = []
        tags_map = {}

        for item in self.dataset.data:
            question_id = item.get('id', 'unknown')
            question = item.get('question', '')
            gold = item.get('gold', {})
            must_cite_sources = gold.get('must_cite_sources', [])
            answer_must_contain = gold.get('answer_must_contain', [])
            tags = item.get('tags', [])
            
            tags_map[question_id] = tags

            embedding = self.llm.embed(question)
            retrieved_docs = self.retriever.retrieve(question, embedding, self.top_k)

            if self.skip_llm:
                answer = ""
            else:
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
                answer = self.llm.generate(prompt)

            metrics_result = EvaluationMetrics.compute_all_metrics(
                question_id=question_id,
                question=question,
                answer=answer,
                retrieved_docs=retrieved_docs,
                must_cite_sources=must_cite_sources,
                answer_must_contain=answer_must_contain,
                k=self.top_k
            )

            question_results.append(metrics_result)

            results['questions'].append({
                'question_id': question_id,
                'question': question,
                'answer': answer if answer else None,
                'retrieved_sources': metrics_result['retrieved_sources'],
                'hit_rate_at_k': metrics_result['hit_rate_at_k'],
                'recall_at_k': metrics_result['recall_at_k'],
                'mrr': metrics_result['mrr'],
                'citation_rate': metrics_result['citation_rate'],
                'contains_rate': metrics_result['contains_rate'],
            })

        aggregated = EvaluationMetrics.aggregate_metrics(question_results)
        results['metrics'] = aggregated

        tag_metrics = EvaluationMetrics.aggregate_by_tag(question_results, tags_map)
        results['tag_metrics'] = tag_metrics

        self.save_results(results)
        return results


class RegressionTestRunner:
    """回归测试运行器"""

    def __init__(self, dataset_path: str = None):
        self.dataset_path = dataset_path or settings.eval_dataset_path
        self.history_file = os.path.join(
            settings.eval_output_path, 
            'regression_history.json'
        )

    def run_regression_test(self, baseline_file: Optional[str] = None) -> Dict[str, Any]:
        """运行回归测试"""
        runner = EvaluationRunner(dataset_path=self.dataset_path)
        
        if baseline_file:
            comparison = runner.compare_with_previous(baseline_file)
        else:
            comparison = runner.compare_with_previous()
        
        self._save_to_history(runner.latest_result_file)
        
        return comparison

    def _save_to_history(self, result_file: str):
        """保存评测历史"""
        os.makedirs(settings.eval_output_path, exist_ok=True)
        
        history = []
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'result_file': result_file,
        })
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def get_history(self) -> List[Dict[str, Any]]:
        """获取评测历史"""
        if not os.path.exists(self.history_file):
            return []
        
        with open(self.history_file, 'r', encoding='utf-8') as f:
            return json.load(f)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CodeRAG Evaluation Runner")
    parser.add_argument('--dataset', type=str, default=None, help="Dataset path")
    parser.add_argument('--top-k', type=int, default=None, help="Top-k for retrieval")
    parser.add_argument('--skip-llm', action='store_true', help="Skip LLM generation (only test retrieval)")
    parser.add_argument('--compare', type=str, default=None, help="Compare with previous results")
    
    args = parser.parse_args()
    
    runner = EvaluationRunner(
        dataset_path=args.dataset,
        top_k=args.top_k,
        skip_llm=args.skip_llm
    )
    
    if args.compare:
        runner.compare_with_previous(args.compare)
    else:
        runner.run_evaluation()
