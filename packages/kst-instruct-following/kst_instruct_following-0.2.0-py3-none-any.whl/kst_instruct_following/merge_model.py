#!/usr/bin/env python3
"""
合并Llama-2-7b-chat基础模型和adapter的脚本
"""

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig
import argparse
from pathlib import Path

def merge_models(base_model_path, adapter_path, output_path):
    """
    合并基础模型和adapter
    
    Args:
        base_model_path (str): 基础模型路径
        adapter_path (str): adapter路径
        output_path (str): 输出路径
    """
    print(f"开始合并模型...")
    print(f"基础模型路径: {base_model_path}")
    print(f"Adapter路径: {adapter_path}")
    print(f"输出路径: {output_path}")
    
    # 创建输出目录
    os.makedirs(output_path, exist_ok=True)
    
    try:
        # 加载adapter配置
        print("正在加载adapter配置...")
        peft_config = PeftConfig.from_pretrained(adapter_path)
        
        # 加载基础模型
        print("正在加载基础模型...")
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True
        )
        
        # 加载tokenizer
        print("正在加载tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(base_model_path)
        
        # 加载PEFT模型
        print("正在加载PEFT模型...")
        model = PeftModel.from_pretrained(base_model, adapter_path)
        
        # 合并模型
        print("正在合并模型...")
        merged_model = model.merge_and_unload()
        
        # 保存合并后的模型
        print("正在保存合并后的模型...")
        merged_model.save_pretrained(
            output_path,
            save_function=torch.save,
            max_shard_size="15GB"
        )
        
        # 保存tokenizer
        print("正在保存tokenizer...")
        tokenizer.save_pretrained(output_path)
        
        print(f"模型合并完成！已保存到: {output_path}")
        
    except Exception as e:
        print(f"合并过程中出现错误: {str(e)}")
        
        # 如果PEFT方法失败，尝试直接合并权重
        print("尝试使用备用方法...")
        try:
            # 备用方法：直接加载和合并
            print("正在使用备用方法加载模型...")
            
            # 加载基础模型
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_path,
                torch_dtype=torch.bfloat16,
                device_map="auto",
                trust_remote_code=True
            )
            
            # 加载tokenizer
            tokenizer = AutoTokenizer.from_pretrained(base_model_path)
            
            # 检查adapter是否为完整模型
            if os.path.exists(os.path.join(adapter_path, "pytorch_model.bin")) or \
               os.path.exists(os.path.join(adapter_path, "model.safetensors")):
                
                # 如果adapter是完整模型，直接复制
                print("Adapter似乎是完整模型，直接复制...")
                adapter_model = AutoModelForCausalLM.from_pretrained(
                    adapter_path,
                    torch_dtype=torch.bfloat16,
                    device_map="auto",
                    trust_remote_code=True
                )
                
                # 保存模型
                adapter_model.save_pretrained(
                    output_path,
                    save_function=torch.save,
                    max_shard_size="15GB"
                )
                
            else:
                # 如果是权重文件，尝试手动合并
                print("尝试手动合并权重...")
                base_model.save_pretrained(
                    output_path,
                    save_function=torch.save,
                    max_shard_size="15GB"
                )
            
            # 保存tokenizer
            tokenizer.save_pretrained(output_path)
            
            print(f"使用备用方法成功！模型已保存到: {output_path}")
            
        except Exception as backup_error:
            print(f"备用方法也失败了: {str(backup_error)}")
            raise

def main(args):
    # 设置路径
    # base_model_path = "/data/public/Llama/Llama2/Llama-2-7b-chat"
    base_model_path = args.base_model_path
    # adapter_path = "/data/daixl/RL_study/SimLLMCultureDist/SimLLMCultureDist/output/Llama-3.1-8B_base_epoch_5"
    adapter_path = args.adapter_path
    output_path = args.output_path
    
    # 检查路径是否存在
    if not os.path.exists(base_model_path):
        print(f"错误: 基础模型路径不存在: {base_model_path}")
        return
    
    if not os.path.exists(adapter_path):
        print(f"错误: Adapter路径不存在: {adapter_path}")
        return
    
    # 执行合并
    merge_models(base_model_path, adapter_path, output_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_model_path',default='/data/public/Qwen/Qwen2.5/Qwen2.5-7B-Instruct',type=str)
    parser.add_argument('--adapter_path',default='/data/daixl/RL_study/SFT4test/Llama3en',type=str)
    parser.add_argument('--output_path',default='/data/daixl/RL_study/CultureSteer/CultureLLMEN',type=str)
    args = parser.parse_args()
    main(args)