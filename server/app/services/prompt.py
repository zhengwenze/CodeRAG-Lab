from typing import List, Dict, Any


class PromptTemplate:
    """Prompt 模板类"""

    @staticmethod
    def rag_prompt(question: str, contexts: List[Dict[str, Any]]) -> str:
        """构建 RAG 提示模板

        Args:
            question: 用户问题
            contexts: 检索到的上下文信息

        Returns:
            构建好的 prompt
        """
        context_str = "\n\n".join([
            f"文件: {ctx.get('file_path', 'unknown')}\n" 
            f"行号: {ctx.get('start_line', 'unknown')}-{ctx.get('end_line', 'unknown')}\n" 
            f"内容: {ctx.get('content', 'empty')}"
            for ctx in contexts
        ])

        prompt = f"""你是一个专业的代码库助手，需要基于提供的代码上下文回答用户问题。

# 上下文信息
{context_str}

# 用户问题
{question}

# 回答要求
1. 基于提供的上下文信息回答问题
2. 保持回答准确、专业
3. 引用相关代码片段时，标明文件路径和行号
4. 如果无法基于上下文回答，请明确说明
5. 回答语言与用户问题语言保持一致
"""

        return prompt

    @staticmethod
    def evaluation_prompt(question: str, contexts: List[Dict[str, Any]]) -> str:
        """构建评测提示模板

        Args:
            question: 评测问题
            contexts: 检索到的上下文信息

        Returns:
            构建好的 prompt
        """
        context_str = "\n\n".join([
            f"文件: {ctx.get('file_path', 'unknown')}\n" 
            f"内容: {ctx.get('content', 'empty')}"
            for ctx in contexts
        ])

        prompt = f"""请基于以下上下文回答问题，只返回答案内容，不要添加任何其他信息。

上下文：
{context_str}

问题：
{question}

答案："""

        return prompt