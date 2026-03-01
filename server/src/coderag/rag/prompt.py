from typing import List, Dict, Any


class PromptTemplate:
    """提示词模板"""

    @staticmethod
    def rag_prompt(query: str, contexts: List[Dict[str, Any]]) -> str:
        """RAG提示词模板"""
        context_str = "\n\n".join([
            f"[文件: {ctx['file_path']}, 行号: {ctx.get('start_line', 'N/A')}-{ctx.get('end_line', 'N/A')}]\n{ctx['content']}"
            for ctx in contexts
        ])

        prompt = f"""
你是一个专业的代码库助手，需要根据提供的代码片段回答用户问题。

请严格遵循以下规则：
1. 只基于提供的代码片段回答问题，不要编造信息
2. 回答要详细、准确，包含必要的代码示例
3. 对于不确定的问题，明确表示不确定
4. 回答结束后，列出你参考的代码片段来源

提供的代码片段：
{context_str}

用户问题：
{query}

请回答：
"""

        return prompt

    @staticmethod
    def citation_prompt() -> str:
        """引用提示词"""
        return "\n\n参考的代码片段："

    @staticmethod
    def evaluation_prompt(question: str, contexts: List[Dict[str, Any]]) -> str:
        """评测提示词模板"""
        context_str = "\n\n".join([
            f"[文件: {ctx['file_path']}]\n{ctx['content']}"
            for ctx in contexts
        ])

        prompt = f"""
请基于以下代码片段回答问题，并判断回答是否正确。

代码片段：
{context_str}

问题：
{question}

回答：
"""

        return prompt