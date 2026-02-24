import click
from coderag.ingest.repo_loader import RepoLoader
from coderag.ingest.chunker import Chunker
from coderag.rag.qdrant_store import QdrantStore
from coderag.llm.provider import LLMProviderFactory
from coderag.settings import settings


@click.group()
def cli():
    """CodeRAG Lab CLI"""
    pass


@cli.command()
@click.argument('repo_path')
def ingest(repo_path):
    """入库代码库"""
    click.echo(f"Ingesting repository: {repo_path}")

    # 加载代码库
    loader = RepoLoader(repo_path)
    files = loader.load()
    click.echo(f"Loaded {len(files)} files")

    # 分块
    chunker = Chunker()
    all_chunks = []
    for file in files:
        chunks = chunker.chunk_file(file['file_path'], file['content'])
        all_chunks.extend(chunks)
    click.echo(f"Created {len(all_chunks)} chunks")

    # 生成嵌入
    llm = LLMProviderFactory.get_provider(settings.llm_provider)
    embedded_chunks = []
    for i, chunk in enumerate(all_chunks):
        if i % 10 == 0:
            click.echo(f"Processing chunk {i}/{len(all_chunks)}")
        embedding = llm.embed(chunk['content'])
        chunk['embedding'] = embedding
        embedded_chunks.append(chunk)
    click.echo(f"Generated embeddings for {len(embedded_chunks)} chunks")

    # 根据配置选择存储
    from coderag.rag.retriever import Retriever
    retriever = Retriever()
    retriever.add_points(embedded_chunks)
    click.echo(f"Ingestion completed successfully using {settings.vector_store}")


@cli.command()
@click.argument('dataset_path')
def eval(dataset_path):
    """运行评测"""
    click.echo(f"Running evaluation on dataset: {dataset_path}")
    from coderag.eval.runner import EvaluationRunner
    runner = EvaluationRunner(dataset_path)
    results = runner.run_evaluation()
    click.echo("Evaluation completed successfully")


@cli.command()
def init():
    """初始化项目"""
    click.echo("Initializing CodeRAG Lab")
    # 创建必要的目录
    import os
    directories = [
        'data/eval',
        'data/runs',
        'data/qdrant_storage',
        'data/ingested',
        'logs',
    ]
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
    click.echo("Initialization completed successfully")


if __name__ == '__main__':
    cli()