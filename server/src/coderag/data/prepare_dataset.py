import json
import os
from typing import List, Dict, Any
import re


class DatasetPreparer:
    """fine_tune数据集准备器"""

    def __init__(self):
        pass

    def from_eval_dataset(self, eval_dataset_path: str, output_path: str) -> None:
        """从评测数据集生成fine_tune数据集"""
        print(f"Converting eval dataset: {eval_dataset_path}")
        
        # 加载评测数据集
        with open(eval_dataset_path, 'r', encoding='utf-8') as f:
            eval_data = json.load(f)
        
        items = eval_data.get("items", [])
        
        # 转换为fine_tune格式
        fine_tune_items = []
        for item in items:
            question = item.get("question", "")
            gold = item.get("gold", {})
            must_cite_sources = gold.get("must_cite_sources", [])
            answer_must_contain = gold.get("answer_must_contain", [])
            
            # 构建上下文
            context = "\n".join([f"Source: {source}" for source in must_cite_sources])
            
            # 构建答案（基于must_contain）
            answer = " ".join(answer_must_contain)
            
            if question and answer:
                fine_tune_items.append({
                    "question": question,
                    "answer": answer,
                    "context": context,
                    "tags": item.get("tags", [])
                })
        
        # 构建输出数据
        output_data = {
            "dataset_name": f"{eval_data.get('dataset_name', 'coderag_eval')}_fine_tune",
            "repo_name": eval_data.get("repo_name", "unknown"),
            "items": fine_tune_items
        }
        
        # 保存输出
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"Generated fine_tune dataset with {len(fine_tune_items)} samples")
        print(f"Saved to: {output_path}")

    def from_codebase(self, repo_path: str, output_path: str, extensions: List[str] = None) -> None:
        """从代码库生成fine_tune数据集"""
        if extensions is None:
            extensions = ['.py', '.md', '.txt']
        
        print(f"Scanning codebase: {repo_path}")
        print(f"Extensions: {extensions}")
        
        fine_tune_items = []
        
        # 遍历代码库
        for root, dirs, files in os.walk(repo_path):
            # 跳过某些目录
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', '.venv']]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                        continue
                    
                    # 从Python文件提取函数和类
                    if file.endswith('.py'):
                        fine_tune_items.extend(self._extract_from_python(relative_path, content))
                    # 从Markdown文件提取标题和内容
                    elif file.endswith('.md'):
                        fine_tune_items.extend(self._extract_from_markdown(relative_path, content))
                    # 从文本文件提取内容
                    else:
                        fine_tune_items.extend(self._extract_from_text(relative_path, content))
        
        # 构建输出数据
        output_data = {
            "dataset_name": "codebase_fine_tune",
            "repo_name": os.path.basename(repo_path),
            "items": fine_tune_items
        }
        
        # 保存输出
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"Generated fine_tune dataset with {len(fine_tune_items)} samples")
        print(f"Saved to: {output_path}")

    def _extract_from_python(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """从Python文件提取fine_tune样本"""
        items = []
        
        # 提取函数定义
        function_pattern = re.compile(r'def\s+(\w+)\s*\(([^)]*)\)\s*:\s*(?:"""(["""|'''[\s\S]*?["""|'''])\s*""")?', re.MULTILINE)
        for match in function_pattern.finditer(content):
            func_name = match.group(1)
            params = match.group(2)
            docstring = match.group(3) or ""
            
            # 构建问题和答案
            question = f"What does the function `{func_name}` do in file `{file_path}`?"
            answer = f"Function `{func_name}({params})` in `{file_path}`: {docstring.strip()}"
            
            items.append({
                "question": question,
                "answer": answer,
                "context": f"File: {file_path}",
                "tags": ["function", "python"]
            })
        
        # 提取类定义
        class_pattern = re.compile(r'class\s+(\w+)\s*(?:\(([^)]*)\))?\s*:\s*(?:"""(["""|'''[\s\S]*?["""|'''])\s*""")?', re.MULTILINE)
        for match in class_pattern.finditer(content):
            class_name = match.group(1)
            bases = match.group(2) or ""
            docstring = match.group(3) or ""
            
            # 构建问题和答案
            question = f"What does the class `{class_name}` do in file `{file_path}`?"
            answer = f"Class `{class_name}({bases})` in `{file_path}`: {docstring.strip()}"
            
            items.append({
                "question": question,
                "answer": answer,
                "context": f"File: {file_path}",
                "tags": ["class", "python"]
            })
        
        return items

    def _extract_from_markdown(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """从Markdown文件提取fine_tune样本"""
        items = []
        
        # 提取标题和内容
        heading_pattern = re.compile(r'(#{1,6})\s+([^\n]+)\n\n([\s\S]*?)(?=\n#{1,6}|$)', re.MULTILINE)
        for match in heading_pattern.finditer(content):
            level = len(match.group(1))
            heading = match.group(2).strip()
            section_content = match.group(3).strip()
            
            # 构建问题和答案
            question = f"What is in the section '{heading}' of file `{file_path}`?"
            answer = section_content[:500]  # 限制长度
            
            items.append({
                "question": question,
                "answer": answer,
                "context": f"File: {file_path}",
                "tags": ["markdown", "documentation"]
            })
        
        return items

    def _extract_from_text(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """从文本文件提取fine_tune样本"""
        items = []
        
        # 简单处理：每1000字符为一个样本
        chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
        for i, chunk in enumerate(chunks):
            question = f"What is in chunk {i+1} of file `{file_path}`?"
            answer = chunk.strip()
            
            items.append({
                "question": question,
                "answer": answer,
                "context": f"File: {file_path}",
                "tags": ["text"]
            })
        
        return items

    def merge_datasets(self, input_paths: List[str], output_path: str) -> None:
        """合并多个fine_tune数据集"""
        print(f"Merging {len(input_paths)} datasets")
        
        all_items = []
        repo_names = set()
        
        for path in input_paths:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            all_items.extend(data.get("items", []))
            repo_names.add(data.get("repo_name", "unknown"))
        
        # 构建输出数据
        output_data = {
            "dataset_name": "merged_fine_tune",
            "repo_name": ", ".join(repo_names),
            "items": all_items
        }
        
        # 保存输出
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"Merged {len(all_items)} samples from {len(input_paths)} datasets")
        print(f"Saved to: {output_path}")

    def split_dataset(self, input_path: str, output_dir: str, train_ratio: float = 0.8) -> None:
        """分割数据集为训练集和验证集"""
        print(f"Splitting dataset: {input_path}")
        
        # 加载数据
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        items = data.get("items", [])
        total = len(items)
        train_size = int(total * train_ratio)
        
        # 分割数据
        train_items = items[:train_size]
        val_items = items[train_size:]
        
        # 保存训练集
        train_data = {
            "dataset_name": f"{data.get('dataset_name', 'fine_tune')}_train",
            "repo_name": data.get("repo_name", "unknown"),
            "items": train_items
        }
        train_path = os.path.join(output_dir, "train.json")
        with open(train_path, 'w', encoding='utf-8') as f:
            json.dump(train_data, f, ensure_ascii=False, indent=2)
        
        # 保存验证集
        val_data = {
            "dataset_name": f"{data.get('dataset_name', 'fine_tune')}_val",
            "repo_name": data.get("repo_name", "unknown"),
            "items": val_items
        }
        val_path = os.path.join(output_dir, "val.json")
        with open(val_path, 'w', encoding='utf-8') as f:
            json.dump(val_data, f, ensure_ascii=False, indent=2)
        
        print(f"Split into {len(train_items)} train and {len(val_items)} val samples")
        print(f"Train saved to: {train_path}")
        print(f"Val saved to: {val_path}")


def get_dataset_preparer() -> DatasetPreparer:
    """获取数据集准备器"""
    return DatasetPreparer()


if __name__ == "__main__":
    # 示例用法
    preparer = DatasetPreparer()
    
    # 1. 从评测数据集生成fine_tune数据集
    # preparer.from_eval_dataset(
    #     "data/eval/coderag_eval_v1.json",
    #     "data/fine_tune/coderag_eval_fine_tune.json"
    # )
    
    # 2. 从代码库生成fine_tune数据集
    # preparer.from_codebase(
    #     "src",
    #     "data/fine_tune/codebase_fine_tune.json"
    # )
    
    # 3. 合并数据集
    # preparer.merge_datasets(
    #     ["data/fine_tune/coderag_eval_fine_tune.json", "data/fine_tune/codebase_fine_tune.json"],
    #     "data/fine_tune/merged_fine_tune.json"
    # )
    
    # 4. 分割数据集
    # preparer.split_dataset(
    #     "data/fine_tune/merged_fine_tune.json",
    #     "data/fine_tune/splits"
    # )
