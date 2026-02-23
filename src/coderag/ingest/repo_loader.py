from typing import List, Dict, Any
import os
import git
from pathlib import Path


class RepoLoader:
    """代码库加载器"""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def load(self) -> List[Dict[str, Any]]:
        """加载代码库文件"""
        files = []
        for root, _, filenames in os.walk(self.repo_path):
            for filename in filenames:
                if self._should_include(filename):
                    file_path = os.path.join(root, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        files.append({
                            'file_path': file_path,
                            'content': content,
                            'file_size': len(content),
                        })
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")
        return files

    def _should_include(self, filename: str) -> bool:
        """判断是否应该包含该文件"""
        # 排除二进制文件和特定目录
        exclude_extensions = ['.pyc', '.exe', '.dll', '.so', '.bin', '.zip', '.tar', '.gz']
        exclude_dirs = ['__pycache__', '.git', 'node_modules', 'venv', '.venv', 'build', 'dist']

        # 检查文件扩展名
        for ext in exclude_extensions:
            if filename.endswith(ext):
                return False

        # 检查文件是否在排除目录中
        for dir_name in exclude_dirs:
            if dir_name in filename:
                return False

        return True

    def clone_repo(self, repo_url: str, target_dir: str) -> bool:
        """克隆代码库"""
        try:
            git.Repo.clone_from(repo_url, target_dir)
            return True
        except Exception as e:
            print(f"Error cloning repo: {e}")
            return False