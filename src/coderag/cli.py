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

    loader = RepoLoader(repo_path)
    files = loader.load()
    click.echo(f"Loaded {len(files)} files")

    chunker = Chunker()
    all_chunks = []
    for file in files:
        chunks = chunker.chunk_file(file['file_path'], file['content'])
        all_chunks.extend(chunks)
    click.echo(f"Created {len(all_chunks)} chunks")

    llm = LLMProviderFactory.get_provider(settings.llm_provider)
    embedded_chunks = []
    for i, chunk in enumerate(all_chunks):
        if i % 10 == 0:
            click.echo(f"Processing chunk {i}/{len(all_chunks)}")
        embedding = llm.embed(chunk['content'])
        chunk['embedding'] = embedding
        embedded_chunks.append(chunk)
    click.echo(f"Generated embeddings for {len(embedded_chunks)} chunks")

    from coderag.rag.retriever import Retriever
    retriever = Retriever()
    retriever.add_points(embedded_chunks)
    click.echo(f"Ingestion completed successfully using {settings.vector_store}")


@cli.command(name='ingest-repo')
@click.argument('repo_path')
def ingest_repo(repo_path):
    """入库代码库（别名）"""
    ingest(repo_path)


@cli.command()
@click.argument('dataset_path', required=False, default=None)
@click.option('--top-k', type=int, default=None, help='Top-k for retrieval')
@click.option('--skip-llm', is_flag=True, help='Skip LLM generation (only test retrieval)')
def eval(dataset_path, top_k, skip_llm):
    """运行评测"""
    from coderag.eval.runner import EvaluationRunner
    
    runner = EvaluationRunner(
        dataset_path=dataset_path,
        top_k=top_k,
        skip_llm=skip_llm
    )
    results = runner.run_evaluation()
    click.echo("Evaluation completed successfully")


@cli.command()
@click.argument('dataset_path', required=False, default=None)
@click.option('--baseline', type=str, default=None, help='Baseline result file to compare with')
def regression(dataset_path, baseline):
    """运行回归测试，对比历史结果"""
    from coderag.eval.runner import RegressionTestRunner
    
    runner = RegressionTestRunner(dataset_path=dataset_path)
    comparison = runner.run_regression_test(baseline_file=baseline)
    
    if comparison.get('regressions'):
        click.echo(f"\n⚠️  Regressions detected: {len(comparison['regressions'])}")
        for reg in comparison['regressions']:
            click.echo(f"  - {reg}")
    else:
        click.echo("\n✅ No regressions detected")


@cli.command()
def init():
    """初始化项目"""
    click.echo("Initializing CodeRAG Lab")
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
