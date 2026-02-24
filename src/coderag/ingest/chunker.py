from typing import List, Dict, Any
from coderag.settings import settings


class Chunker:
    """代码分块器"""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

    def chunk_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """对文件内容进行分块"""
        chunks = []
        
        if not content:
            return chunks
        
        effective_chunk_size = min(self.chunk_size, len(content))
        effective_overlap = min(self.chunk_overlap, effective_chunk_size - 1) if effective_chunk_size > 1 else 0
            
        lines = content.split('\n')
        total_lines = len(lines)
        
        if total_lines == 1:
            if len(content) > self.chunk_size:
                start = 0
                while start < len(content):
                    end = min(start + effective_chunk_size, len(content))
                    chunk_content = content[start:end]
                    chunk = {
                        'file_path': file_path,
                        'start_line': start + 1,
                        'end_line': end,
                        'content': chunk_content,
                        'chunk_size': len(chunk_content),
                    }
                    chunks.append(chunk)
                    start = end - effective_overlap
                    if start <= chunks[-1]['start_line'] - 1:
                        start = chunks[-1]['end_line']
                    if start >= len(content):
                        break
            else:
                chunk = {
                    'file_path': file_path,
                    'start_line': 1,
                    'end_line': 1,
                    'content': content,
                    'chunk_size': len(content),
                }
                chunks.append(chunk)
            return chunks

        start_line = 1
        while start_line <= total_lines:
            end_line = min(start_line + effective_chunk_size - 1, total_lines)
            
            chunk_content = '\n'.join(lines[start_line-1:end_line])
            
            chunk = {
                'file_path': file_path,
                'start_line': start_line,
                'end_line': end_line,
                'content': chunk_content,
                'chunk_size': len(chunk_content),
            }
            chunks.append(chunk)
            
            start_line = end_line - effective_overlap + 1
            if start_line <= chunks[-1]['start_line']:
                start_line = chunks[-1]['end_line'] + 1
            if start_line > total_lines:
                break

        return chunks

    def chunk_by_function(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """按函数分块（简单实现）"""
        chunks = []
        lines = content.split('\n')
        total_lines = len(lines)

        in_function = False
        function_start = 0
        function_name = ""

        for i, line in enumerate(lines):
            line_num = i + 1
            stripped_line = line.strip()

            # 检测函数定义
            if stripped_line.startswith('def '):
                # 如果已经在函数内，先结束上一个函数
                if in_function:
                    chunk = {
                        'file_path': file_path,
                        'start_line': function_start,
                        'end_line': line_num - 1,
                        'content': '\n'.join(lines[function_start-1:line_num-1]),
                        'function_name': function_name,
                    }
                    chunks.append(chunk)
                
                # 开始新函数
                in_function = True
                function_start = line_num
                function_name = stripped_line.split('(')[0].replace('def ', '')

        # 处理最后一个函数
        if in_function:
            chunk = {
                'file_path': file_path,
                'start_line': function_start,
                'end_line': total_lines,
                'content': '\n'.join(lines[function_start-1:]),
                'function_name': function_name,
            }
            chunks.append(chunk)

        return chunks