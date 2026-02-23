import json
import os
from datetime import datetime
from typing import List, Dict, Any
from coderag.settings import settings
from coderag.eval.dataset import EvaluationDataset
from coderag.eval.metrics import EvaluationMetrics
from coderag.llm.provider import LLMProviderFactory
from coderag.rag.retriever import Retriever


class EvaluationRunner:
    """评测运行器"""

    def __init__(self, dataset_path: str = None, top_k: int = None):
        self.dataset_path = dataset_path or settings.eval_dataset_path
        self.top_k = top_k or settings.top_k
        self.dataset = EvaluationDataset(self.dataset_path)
        self.llm = LLMProviderFactory.get_provider(settings.llm_provider)
        self.retriever = Retriever()

    def run_evaluation(self) -> Dict[str, Any]:
        """运行完整评测"""
        print(f"Running evaluation on dataset: {self.dataset_path}")
        print(f"Top-k: {self.top_k}")

        # 评测结果
        results = {
            'questions': [],
            'metrics': {},
            'timestamp': datetime.utcnow().isoformat(),
        }

        # 计算指标
        recall_scores = []
        mrr_scores = []
        predicted_answers = []
        ground_truths = []
        no_reference_answers = []

        for item in self.dataset.data:
            question = item['question']
            ground_truth = item.get('ground_truth', '')
            relevant_docs = item.get('relevant_docs', [])

            # 生成嵌入
            embedding = self.llm.embed(question)

            # 检索
            retrieved_docs = self.retriever.retrieve(question, embedding, self.top_k)

            # 计算检索指标
            recall = EvaluationMetrics.recall_at_k(relevant_docs, retrieved_docs, self.top_k)
            mrr = EvaluationMetrics.mrr(relevant_docs, retrieved_docs)
            recall_scores.append(recall)
            mrr_scores.append(mrr)

            # 生成回答（暂时跳过）
            # prompt = PromptTemplate.rag_prompt(question, retrieved_docs)
            # answer = self.llm.generate(prompt)
            # predicted_answers.append(answer)
            # ground_truths.append(ground_truth)
            # no_reference_answers.append({'references': retrieved_docs})

            # 记录结果
            results['questions'].append({
                'question': question,
                'ground_truth': ground_truth,
                'relevant_docs': relevant_docs,
                'retrieved_docs': retrieved_docs,
                'recall_at_k': recall,
                'mrr': mrr,
            })

        # 计算平均指标
        avg_recall = sum(recall_scores) / len(recall_scores) if recall_scores else 0.0
        avg_mrr = sum(mrr_scores) / len(mrr_scores) if mrr_scores else 0.0
        # avg_accuracy = EvaluationMetrics.accuracy(predicted_answers, ground_truths) if predicted_answers else 0.0
        # no_reference_rate = EvaluationMetrics.no_reference_rate(no_reference_answers) if no_reference_answers else 0.0

        results['metrics'] = {
            'recall_at_k': avg_recall,
            'mrr': avg_mrr,
            # 'accuracy': avg_accuracy,
            # 'no_reference_rate': no_reference_rate,
        }

        # 保存评测结果
        self.save_results(results)

        # 打印结果
        print("\nEvaluation Results:")
        print(f"Recall@{self.top_k}: {avg_recall:.4f}")
        print(f"MRR: {avg_mrr:.4f}")
        # print(f"Accuracy: {avg_accuracy:.4f}")
        # print(f"No Reference Rate: {no_reference_rate:.4f}")

        return results

    def save_results(self, results: Dict[str, Any]):
        """保存评测结果"""
        output_dir = settings.eval_output_path
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"eval_result_{timestamp}.json")

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Evaluation results saved to: {output_file}")
        except Exception as e:
            print(f"Error saving results: {e}")


if __name__ == "__main__":
    runner = EvaluationRunner()
    runner.run_evaluation()