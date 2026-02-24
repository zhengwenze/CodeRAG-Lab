from typing import List, Dict, Any, Optional, Tuple
import re
from coderag.settings import settings


class Chunker:
    """代码分块器，支持多种分块策略"""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

    def chunk_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """对文件内容进行分块（默认按函数/类分块）"""
        ext = file_path.split('.')[-1].lower()
        
        if ext == 'py':
            return self.chunk_python_by_structure(file_path, content)
        else:
            return self.chunk_by_fixed_size(file_path, content)

    def chunk_python_by_structure(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """按 Python 代码结构（类/函数）智能分块"""
        chunks = []
        lines = content.split('\n')
        total_lines = len(lines)
        
        if total_lines == 0:
            return chunks
        
        structures = self._parse_python_structure(content)
        
        if not structures:
            return self.chunk_by_fixed_size(file_path, content)
        
        for i, struct in enumerate(structures):
            start_line = struct['start_line']
            end_line = struct['end_line']
            
            struct_content = '\n'.join(lines[start_line-1:end_line])
            
            if len(struct_content.strip()) < 50:
                continue
            
            chunk = {
                'file_path': file_path,
                'start_line': start_line,
                'end_line': end_line,
                'content': struct_content,
                'chunk_size': len(struct_content),
                'structure_type': struct['type'],
                'structure_name': struct['name'],
            }
            chunks.append(chunk)
        
        if not chunks:
            return self.chunk_by_fixed_size(file_path, content)
        
        return chunks

    def _parse_python_structure(self, content: str) -> List[Dict[str, Any]]:
        """解析 Python 代码结构，提取类、函数、异步函数"""
        structures = []
        lines = content.split('\n')
        total_lines = len(lines)
        
        i = 0
        while i < total_lines:
            line = lines[i]
            stripped = line.strip()
            
            class_match = re.match(r'^class\s+(\w+)', stripped)
            if class_match:
                class_name = class_match.group(1)
                end_line = self._find_block_end(lines, i, 'class')
                structures.append({
                    'type': 'class',
                    'name': class_name,
                    'start_line': i + 1,
                    'end_line': end_line,
                })
                i = end_line
                continue
            
            func_match = re.match(r'^(async\s+)?def\s+(\w+)', stripped)
            if func_match:
                func_name = func_match.group(2)
                end_line = self._find_block_end(lines, i, 'def', func_match.group(1) == 'async')
                structures.append({
                    'type': 'function' if not func_match.group(1) else 'async_function',
                    'name': func_name,
                    'start_line': i + 1,
                    'end_line': end_line,
                })
                i = end_line
                continue
            
            i += 1
        
        structures.sort(key=lambda x: x['start_line'])
        return structures

    def _find_block_end(self, lines: List[str], start_idx: int, block_type: str, is_async: bool = False) -> int:
        """找到代码块的结束行"""
        total_lines = len(lines)
        base_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip()) if lines[start_idx].strip() else 0
        
        i = start_idx + 1
        while i < total_lines:
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            
            current_indent = len(line) - len(line.lstrip())
            
            if current_indent <= base_indent and line.strip():
                return i
            
            i += 1
        
        return total_lines

    def chunk_by_fixed_size(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """按固定大小分块（fallback 方案）"""
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