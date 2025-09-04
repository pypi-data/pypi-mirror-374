import torch
from transformers import AutoModelForSequenceClassification,AutoTokenizer
from transformers import Trainer, TrainingArguments
from peft import get_peft_model, LoraConfig
from trl import SFTConfig, SFTTrainer
from datasets import load_dataset
import argparse
import os
import json
try:
    from instruct_following_project.src.processor import think_process,sft_system_prompt_process,flatten_process,rm_system_prompt_process

except:
    from processor import think_process,sft_system_prompt_process,flatten_process,rm_system_prompt_process


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--enable_think',action='store_true',default=False,help='是否启用思考过程')
    parser.add_argument('--local_rank', type=int, default=3, help='Local rank for distributed training')
    args = parser.parse_args()
    data_dir = '../dataset'
    model_path = '/data1/public/Qwen/Qwen3/Qwen3-8B'
    # departments = ['fck','yk','erk']
    department = 'yk'
    # train_files = [os.path.join(data_dir,f'{depart}','sft',f'{depart}_sft_train.jsonl') for depart in departments]
    # dev_files = [os.path.join(data_dir,f'{depart}','sft',f'{depart}_sft_dev.jsonl') for depart in departments]
    train_files = os.path.join(data_dir,f'{department}','grpo',f'{department}_grpo_train_scores_sonnet.jsonl')
    dev_files = os.path.join(data_dir,f'{department}','grpo',f'{department}_grpo_dev_scores_sonnet.jsonl')
    train_dataset = load_dataset('json', data_files=train_files)['train']
    dev_dataset = load_dataset('json', data_files=dev_files)['train']
    train_dataset = flatten_process(train_dataset)
    dev_dataset = flatten_process(dev_dataset)
    print(f'train_dataset_size:{len(train_dataset)}')
    print(f'dev_dataset_size:{len(dev_dataset)}')
    if 'Qwen3' in model_path and not args.enable_think:
        train_dataset = train_dataset.map(think_process, num_proc=8)
        dev_dataset = dev_dataset.map(think_process, num_proc=8)
    # train_dataset = train_dataset.select(range(len(train_dataset))) # 打乱
    ori_columns = train_dataset.column_names
    train_dataset = train_dataset.map(rm_system_prompt_process, num_proc=1, remove_columns=ori_columns)
    dev_dataset = dev_dataset.map(rm_system_prompt_process, num_proc=1, remove_columns=ori_columns)
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True,
        use_fast=False,
    )
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    sft_config = SFTConfig(
        output_dir=f'../output/sft_qwen3',
        logging_steps=2,
        max_grad_norm=0.5,
        report_to="swanlab",
        
        per_device_train_batch_size=2,
        gradient_accumulation_steps=32,

        num_train_epochs=5,  #训练5个epoch

        save_steps=100,
        eval_steps=1000,

        max_length=2048,
        packing=True,
        dataloader_pin_memory=False,  # 避免内存问题
        remove_unused_columns=False,   # 保持数据完整性
        
        dataset_num_proc=8
    )

    peft_config = LoraConfig(
        base_model_name_or_path=model_path,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj", "lm_head"], 
        r=8,
        lora_alpha=16,
        lora_dropout=0.1,
        use_rslora=True,
        bias="none",
        task_type="CAUSAL_LM",
        use_dora=True,  # 使用DORA
    )

    print("Loading model...")
    model = AutoModelForSequenceClassification.from_pretrained(
        model_path,
        num_labels=5,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map="auto",  # 让transformers自动分配设备
    )
    model = get_peft_model(model, peft_config)

    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        eval_dataset=dev_dataset,
        args=sft_config,
        processing_class=tokenizer
        
    )

    print("Starting training...")
    trainer.train()
    