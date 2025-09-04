import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,7"
os.environ["SWANLAB_PROJECT"]="instruction_following_grpo"
from trl import GRPOConfig, GRPOTrainer
from datasets import load_dataset,concatenate_datasets
import sys
from transformers import AutoTokenizer, AutoModelForCausalLM,TrainingArguments
import random
from datasets import Features, Sequence, Value, Dataset
import torch
import copy
import argparse
from peft import get_peft_model, LoraConfig, PeftModel
try:
    from instruct_following_project.src.template import reward_template, system_template
    from instruct_following_project.src.grpo_rewarder import GRPO_Rewarder, GRPO_Formater
    from instruct_following_project.src.processor import grpo_system_prompt_process
except:
    from template import reward_template, system_template
    from grpo_rewarder import GRPO_Rewarder, GRPO_Formater
    from processor import grpo_system_prompt_process
# 临时的torch.load的补丁



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--beta', type=float, default=0.1, help='DPO的beta参数') # 0.1-0.5 0.1越靠近模型 0.5越靠近数据
    # parser.add_argument('--train_ratio',default=0.4,type=float)
    # parser.add_argument('--nodebug',action='store_true',default=False)
    parser.add_argument('--output_dir',default='./grpo_output_v4',type=str)
    parser.add_argument('--local_rank', type=int, default=-1, help='Local rank for distributed training')
    parser.add_argument('--deepspeed', type=str, default=None)
    args = parser.parse_args()
    args.output_dir = '../output/grpo'
    print(f'gpu available number: {torch.cuda.device_count()}')
    model_path = '../save_models/sft_qwen3'
    print('-'*20)
    print(f'now loading model from path: {model_path}',flush=True)

    # department = ['fck','yk']
    department = ['yk']
    data_dir = '../dataset/yk/grpo'
    train_files = [f'../dataset/{depart}/grpo/{depart}_grpo_train_augument.jsonl' for depart in department]
    dev_files = [f'../dataset/{depart}/grpo/{depart}_grpo_dev_augument.jsonl' for depart in department]

    train_dataset = load_dataset('json',data_files= train_files)['train']
    dev_dataset = load_dataset('json',data_files= dev_files)['train']
    # fck_dev_dataset = load_dataset('json',data_files=dev_files[0])['train']
    # yk_dev_dataset = load_dataset('json',data_files=dev_files[1])['train']
    # train_size = len(train_dataset)
    # train_ratio_select = args.train_ratio * train_size
    # train_dataset = train_dataset.select(random.sample(range(len(train_dataset)), int(train_ratio_select)))

    train_dataset = train_dataset.map(grpo_system_prompt_process,num_proc=8)
    dev_dataset = dev_dataset.map(grpo_system_prompt_process,num_proc=8)
    train_dataset = concatenate_datasets([train_dataset,dev_dataset])
    train_dataset = train_dataset.shuffle(seed=42)  # 打乱数据集

    # print('Randomly select train_dataset size:', int(train_ratio_select))
    print('-'*20)

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("Loading model with fp16...")
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        device_map="cuda",
        trust_remote_code=True
    )
    
    peft_config = LoraConfig(
        base_model_name_or_path=model_path,
        r=8,
        lora_alpha=16,
        lora_dropout=0.2,
        use_rslora=True,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )
    print("Applying PEFT configuration...")
    model = get_peft_model(model, peft_config)

    training_args=GRPOConfig(
        remove_unused_columns=False,
        fp16=False,
        bf16=True,
        max_prompt_length=2048,  # prompt长度
        max_completion_length=256,  # completion长度
        num_generations=8,
        shuffle_dataset=True,
        temperature=0.9,
        top_p=0.95,
        repetition_penalty=1.0,
        learning_rate=1e-6,
        beta=0.04,
        num_iterations=1,
        epsilon=0.2,
        epsilon_high=0.28,
        scale_rewards=False, # work better
        # reward_weights=[0.35,0.3,0.35], # 打分模型、action跟随、格式化分别占比


        loss_type='bnpo',
        mask_truncated_completions=True,
        per_device_train_batch_size=2,  # 减少批大小
        gradient_accumulation_steps=16,  # 相应增加梯度累积

        deepspeed="../../DeepSpeed_Config/ds_zero1_example.json",
        dataloader_pin_memory=False,  # 减少内存占用

        save_steps=50, 
        save_strategy="steps",  # 确保按步数保存    
        save_total_limit=None,           
        eval_steps=500,

        output_dir=args.output_dir,

        logging_steps=10,           # 更频繁的日志
        logging_dir="./logs",
        logging_first_step=True,
        log_level="info",     

        report_to="swanlab", 

        num_train_epochs=5,  # 新增 epoch 设置
        # use_vllm=True,
        # vllm_server_port=8888,
        # vllm_server_timeout=120.0,
    )

    GRPO_formater = GRPO_Formater()
    # GRPO_rewarder = GRPO_Rewarder('anthropic/claude-sonnet-4',GRPO_formater,training_args,enable_thinking=False)
    
    GRPO_rewarder = GRPO_Rewarder('anthropic/claude-opus-4.1',False,GRPO_formater,training_args,enable_thinking=False,port=8892)
    Trainer = GRPOTrainer(
        model=model,
        reward_funcs=GRPO_rewarder.get_batch_score,
        args=training_args,
        train_dataset=train_dataset,
        # eval_dataset=dev_dataset,
        processing_class=tokenizer,
        # peft_config=peft_config
    )
    print("Starting training...")
    Trainer.train()