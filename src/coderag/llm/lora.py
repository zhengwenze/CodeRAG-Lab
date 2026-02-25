from typing import Dict, List, Optional, Tuple
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, PeftModel
from datasets import Dataset
import json
import os


class LoRATrainer:
    """LoRA微调训练器"""

    def __init__(self):
        pass

    def load_model(self, model_name_or_path: str, device: str = "cpu") -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """加载预训练模型"""
        print(f"Loading model: {model_name_or_path} on {device}")
        model = AutoModelForCausalLM.from_pretrained(model_name_or_path)
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            model.config.pad_token_id = model.config.eos_token_id
        
        model.to(device)
        return model, tokenizer

    def get_lora_config(self, **kwargs) -> LoraConfig:
        """获取LoRA配置"""
        config = LoraConfig(
            r=kwargs.get("r", 8),
            lora_alpha=kwargs.get("lora_alpha", 16),
            target_modules=kwargs.get("target_modules", ["q_proj", "v_proj"]),
            lora_dropout=kwargs.get("lora_dropout", 0.1),
            bias=kwargs.get("bias", "none"),
            task_type=kwargs.get("task_type", "CAUSAL_LM")
        )
        return config

    def prepare_model_for_lora(self, model: AutoModelForCausalLM, lora_config: LoraConfig) -> PeftModel:
        """为模型添加LoRA层"""
        peft_model = get_peft_model(model, lora_config)
        print(f"LoRA model prepared with {sum(p.numel() for p in peft_model.parameters() if p.requires_grad)} trainable parameters")
        return peft_model

    def load_dataset(self, dataset_path: str) -> Dataset:
        """加载微调数据集"""
        print(f"Loading dataset from: {dataset_path}")
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        items = data.get("items", [])
        
        # 准备训练数据
        train_data = []
        for item in items:
            question = item.get("question", "")
            answer = item.get("answer", "")
            context = item.get("context", "")
            
            # 构建训练样本
            if question and answer:
                if context:
                    prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
                else:
                    prompt = f"Question: {question}\n\nAnswer:"
                
                train_data.append({
                    "prompt": prompt,
                    "completion": answer
                })
        
        dataset = Dataset.from_list(train_data)
        print(f"Loaded dataset with {len(dataset)} samples")
        return dataset

    def tokenize_function(self, examples: Dict, tokenizer: AutoTokenizer, max_length: int = 1024) -> Dict:
        """ tokenize函数"""
        texts = [f"{ex['prompt']} {ex['completion']} {tokenizer.eos_token}" for ex in examples]
        tokenized = tokenizer(
            texts,
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt"
        )
        tokenized["labels"] = tokenized["input_ids"].clone()
        return tokenized

    def train(self, 
              model_name_or_path: str, 
              dataset_path: str, 
              output_dir: str, 
              **train_kwargs) -> PeftModel:
        """训练LoRA模型"""
        # 加载模型
        device = train_kwargs.get("device", "cuda" if torch.cuda.is_available() else "cpu")
        model, tokenizer = self.load_model(model_name_or_path, device)
        
        # 准备LoRA配置
        lora_config = self.get_lora_config(**train_kwargs.get("lora_config", {}))
        peft_model = self.prepare_model_for_lora(model, lora_config)
        
        # 加载和处理数据集
        dataset = self.load_dataset(dataset_path)
        tokenized_dataset = dataset.map(
            lambda ex: self.tokenize_function(ex, tokenizer, train_kwargs.get("max_length", 1024)),
            batched=True,
            remove_columns=dataset.column_names
        )
        
        # 准备训练参数
        training_args = TrainingArguments(
            output_dir=output_dir,
            per_device_train_batch_size=train_kwargs.get("batch_size", 4),
            gradient_accumulation_steps=train_kwargs.get("gradient_accumulation_steps", 1),
            learning_rate=train_kwargs.get("learning_rate", 1e-4),
            num_train_epochs=train_kwargs.get("num_epochs", 3),
            weight_decay=train_kwargs.get("weight_decay", 0.01),
            logging_dir=os.path.join(output_dir, "logs"),
            logging_steps=train_kwargs.get("logging_steps", 10),
            save_strategy=train_kwargs.get("save_strategy", "epoch"),
            save_total_limit=train_kwargs.get("save_total_limit", 2),
            load_best_model_at_end=train_kwargs.get("load_best_model_at_end", False),
            warmup_ratio=train_kwargs.get("warmup_ratio", 0.03),
            fp16=train_kwargs.get("fp16", torch.cuda.is_available()),
            optim=train_kwargs.get("optim", "adamw_torch"),
        )
        
        # 数据收集器
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False
        )
        
        # 创建训练器
        trainer = Trainer(
            model=peft_model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )
        
        # 开始训练
        print("Starting LoRA training...")
        trainer.train()
        print("Training completed!")
        
        # 保存模型
        peft_model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        print(f"Model saved to: {output_dir}")
        
        return peft_model

    def merge_and_save_model(self, 
                            base_model_path: str, 
                            peft_model_path: str, 
                            output_dir: str) -> None:
        """合并并保存模型"""
        print(f"Merging model: {base_model_path} + {peft_model_path}")
        
        # 加载基础模型
        base_model, tokenizer = self.load_model(base_model_path)
        
        # 加载Peft模型
        peft_model = PeftModel.from_pretrained(base_model, peft_model_path)
        
        # 合并模型
        merged_model = peft_model.merge_and_unload()
        
        # 保存合并后的模型
        merged_model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        print(f"Merged model saved to: {output_dir}")

    def generate_with_model(self, 
                          model: AutoModelForCausalLM, 
                          tokenizer: AutoTokenizer, 
                          prompt: str, 
                          **generate_kwargs) -> str:
        """使用模型生成回答"""
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        outputs = model.generate(
            **inputs,
            max_new_tokens=generate_kwargs.get("max_new_tokens", 512),
            temperature=generate_kwargs.get("temperature", 0.7),
            top_p=generate_kwargs.get("top_p", 0.95),
            num_return_sequences=generate_kwargs.get("num_return_sequences", 1),
            do_sample=generate_kwargs.get("do_sample", True),
        )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response


class LoRAProvider:
    """LoRA模型提供者"""

    def __init__(self, model_path: str, device: str = "cpu"):
        self.model_path = model_path
        self.device = device
        self.model = None
        self.tokenizer = None
        self._load_model()

    def _load_model(self):
        """加载模型"""
        print(f"Loading LoRA model from: {self.model_path}")
        
        # 检查是否是Peft模型
        if os.path.exists(os.path.join(self.model_path, "adapter_config.json")):
            # 这是一个Peft模型
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from peft import PeftModel
            
            # 尝试从adapter_config.json获取基础模型
            adapter_config_path = os.path.join(self.model_path, "adapter_config.json")
            if os.path.exists(adapter_config_path):
                with open(adapter_config_path, 'r') as f:
                    config = json.load(f)
                base_model_name = config.get("base_model_name_or_path", "mistralai/Mistral-7B-v0.1")
            else:
                base_model_name = "mistralai/Mistral-7B-v0.1"
            
            # 加载基础模型
            base_model = AutoModelForCausalLM.from_pretrained(base_model_name)
            tokenizer = AutoTokenizer.from_pretrained(base_model_name)
            
            # 加载Peft模型
            self.model = PeftModel.from_pretrained(base_model, self.model_path)
            self.tokenizer = tokenizer
        else:
            # 这是一个完整的模型
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self.model, self.tokenizer = LoRATrainer().load_model(self.model_path, self.device)
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.model.config.eos_token_id
        
        self.model.to(self.device)
        print(f"Model loaded successfully on {self.device}")

    def generate(self, prompt: str, **kwargs) -> str:
        """生成回答"""
        if self.model is None or self.tokenizer is None:
            self._load_model()
        
        return LoRATrainer().generate_with_model(self.model, self.tokenizer, prompt, **kwargs)

    def stream_generate(self, prompt: str, **kwargs) -> str:
        """流式生成回答"""
        # 简化实现，返回完整回答
        return self.generate(prompt, **kwargs)

    def embed(self, text: str) -> List[float]:
        """生成文本嵌入"""
        # 使用sentence-transformers
        from coderag.llm.embedding import get_embedding_provider
        provider = get_embedding_provider()
        return provider.embed(text)


def get_lora_trainer() -> LoRATrainer:
    """获取LoRA训练器"""
    return LoRATrainer()


def get_lora_provider(model_path: str, device: str = "cpu") -> LoRAProvider:
    """获取LoRA模型提供者"""
    return LoRAProvider(model_path, device)
