from typing import Dict, Any, List
from datetime import datetime
from app.config import settings
from app.utils.logging import get_logger
from coderag.eval.runner import EvaluationRunner as CoreEvaluationRunner

logger = get_logger(__name__)


class EvaluationRunner:
    """评测运行器 - 包装核心评测逻辑"""

    def __init__(self, dataset_path: str, top_k: int = 5, skip_llm: bool = True):
        """初始化评测运行器

        Args:
            dataset_path: 评测数据集路径
            top_k: 检索结果数量
            skip_llm: 是否跳过 LLM 生成
        """
        self.core_runner = CoreEvaluationRunner(
            dataset_path=dataset_path,
            top_k=top_k,
            skip_llm=skip_llm
        )
        logger.info(f"Initialized EvaluationRunner with dataset: {dataset_path}")

    def run_evaluation(self) -> Dict[str, Any]:
        """运行评测

        Returns:
            评测结果
        """
        try:
            results = self.core_runner.run_evaluation()
            logger.info("Evaluation completed successfully")
            return results
        except Exception as e:
            logger.error(f"Error running evaluation: {e}", exc_info=e)
            return {}