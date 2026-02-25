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


@cli.group(name='lora')
def lora_group():
    """LoRA微调相关命令"""
    pass


@lora_group.command(name='train')
@click.argument('model_path')
@click.argument('dataset_path')
@click.argument('output_path')
@click.option('--r', type=int, default=8, help='LoRA rank')
@click.option('--lora-alpha', type=int, default=16, help='LoRA alpha')
@click.option('--batch-size', type=int, default=4, help='Batch size')
@click.option('--num-epochs', type=int, default=3, help='Number of epochs')
@click.option('--learning-rate', type=float, default=1e-4, help='Learning rate')
@click.option('--device', type=str, default=None, help='Device to use')
def lora_train(model_path, dataset_path, output_path, r, lora_alpha, batch_size, num_epochs, learning_rate, device):
    """训练LoRA模型"""
    from coderag.llm.lora import get_lora_trainer
    import torch
    
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    click.echo(f"Training LoRA model: {model_path}")
    click.echo(f"Dataset: {dataset_path}")
    click.echo(f"Output: {output_path}")
    click.echo(f"Device: {device}")
    
    trainer = get_lora_trainer()
    trainer.train(
        model_name_or_path=model_path,
        dataset_path=dataset_path,
        output_dir=output_path,
        lora_config={
            "r": r,
            "lora_alpha": lora_alpha
        },
        batch_size=batch_size,
        num_epochs=num_epochs,
        learning_rate=learning_rate,
        device=device
    )
    click.echo("LoRA training completed successfully")


@lora_group.command(name='prepare-dataset')
@click.argument('input_path')
@click.argument('output_path')
@click.option('--from', 'from_type', type=click.Choice(['eval', 'codebase']), default='eval', help='Dataset source type')
@click.option('--extensions', type=str, default='.py,.md,.txt', help='File extensions for codebase')
def lora_prepare_dataset(input_path, output_path, from_type, extensions):
    """准备微调数据集"""
    from coderag.data.prepare_dataset import get_dataset_preparer
    
    click.echo(f"Preparing dataset from {from_type}: {input_path}")
    
    preparer = get_dataset_preparer()
    
    if from_type == 'eval':
        preparer.from_eval_dataset(input_path, output_path)
    elif from_type == 'codebase':
        extensions_list = [ext.strip() for ext in extensions.split(',')]
        preparer.from_codebase(input_path, output_path, extensions_list)
    
    click.echo("Dataset preparation completed successfully")


@lora_group.command(name='merge')
@click.argument('base_model_path')
@click.argument('peft_model_path')
@click.argument('output_path')
def lora_merge(base_model_path, peft_model_path, output_path):
    """合并LoRA模型"""
    from coderag.llm.lora import get_lora_trainer
    
    click.echo(f"Merging models: {base_model_path} + {peft_model_path}")
    
    trainer = get_lora_trainer()
    trainer.merge_and_save_model(base_model_path, peft_model_path, output_path)
    
    click.echo("Model merging completed successfully")


@lora_group.command(name='generate')
@click.argument('model_path')
@click.argument('prompt')
@click.option('--device', type=str, default=None, help='Device to use')
@click.option('--max-new-tokens', type=int, default=512, help='Max new tokens')
@click.option('--temperature', type=float, default=0.7, help='Temperature')
def lora_generate(model_path, prompt, device, max_new_tokens, temperature):
    """使用LoRA模型生成回答"""
    from coderag.llm.lora import get_lora_provider
    import torch
    
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    click.echo(f"Generating with model: {model_path}")
    click.echo(f"Device: {device}")
    
    provider = get_lora_provider(model_path, device)
    response = provider.generate(
        prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature
    )
    
    click.echo("\n=== Response ===")
    click.echo(response)
    click.echo("================")


@lora_group.command(name='split-dataset')
@click.argument('input_path')
@click.argument('output_dir')
@click.option('--train-ratio', type=float, default=0.8, help='Train ratio')
def lora_split_dataset(input_path, output_dir, train_ratio):
    """分割数据集为训练集和验证集"""
    from coderag.data.prepare_dataset import get_dataset_preparer
    
    click.echo(f"Splitting dataset: {input_path}")
    
    preparer = get_dataset_preparer()
    preparer.split_dataset(input_path, output_dir, train_ratio)
    
    click.echo("Dataset splitting completed successfully")


@lora_group.command(name='merge-datasets')
@click.argument('output_path')
@click.argument('input_paths', nargs=-1)
def lora_merge_datasets(output_path, input_paths):
    """合并多个微调数据集"""
    from coderag.data.prepare_dataset import get_dataset_preparer
    
    click.echo(f"Merging {len(input_paths)} datasets")
    
    preparer = get_dataset_preparer()
    preparer.merge_datasets(list(input_paths), output_path)
    
    click.echo("Dataset merging completed successfully")


@lora_group.command(name='compare')
@click.argument('lora_model_path')
@click.option('--dataset', type=str, default=None, help='Dataset path')
@click.option('--top-k', type=int, default=None, help='Top-k for retrieval')
def lora_compare(lora_model_path, dataset, top_k):
    """对比评测微调与原始模型"""
    from coderag.eval.lora_comparison import LoRAComparisonRunner
    
    click.echo(f"Running LoRA comparison evaluation")
    click.echo(f"LoRA model: {lora_model_path}")
    click.echo(f"Dataset: {dataset or 'default'}")
    
    runner = LoRAComparisonRunner(
        dataset_path=dataset,
        top_k=top_k,
        lora_model_path=lora_model_path
    )
    runner.run_comparison()
    
    click.echo("LoRA comparison evaluation completed successfully")


if __name__ == '__main__':
    cli()
