from grpo_rewarder import get_prompt_score, GRPO_Formater
from datasets import load_dataset, concatenate_datasets
from functools import partial
from transformers import AutoModelForCausalLM, AutoTokenizer
from kst_instruct_following.template.reward_template import strategy_reward_model_template, output_format, concat_generate_completions, concat_instructions
from kst_instruct_following.processor import grpo_system_prompt_process, think_process, score_process
import os
from functools import partial
def generate_completion(example):
    pass



if __name__ == '__main__':
    department = ['yk']
    data_dir = '../dataset/yk/grpo'
    dev_files = [f'../dataset/{depart}/grpo/{depart}_grpo_dev_augument.jsonl' for depart in department]
    dev_dataset = load_dataset('json',data_files= dev_files)['train']

    # dev_dataset = dev_dataset.select(range(5)) # 选择子集进行测试
    
    # 先获取模型的回复 (isgenerate=True)
    _get_model_completion = partial(get_prompt_score, model='', tokenizer='', isrouter_key=False, enable_thinking=False, score_batch=4, isstop=True, port=8890, G=4,isgenerate=True)

    dev_dataset = dev_dataset.map(think_process, num_proc=1,load_from_cache_file=False) # 改为think格式

    dev_dataset = dev_dataset.map(grpo_system_prompt_process,num_proc=1) # 添加grpo的系统提示

    dev_dataset = dev_dataset.map(_get_model_completion, num_proc=16,load_from_cache_file=False)
    # 保存结果
    write_path = os.path.join(data_dir,'yk_grpo_dev_completions.jsonl')
    dev_dataset.to_json(write_path,lines=True,orient='records',force_ascii=False)


    # 第二步，转换为GRPO的生成格式 -- 一个prompt对应一个completion -- 然后使用cluade打分

    # completions存放四个回复
    # 首先对每条数据 处理成打分template的形式

    write_path = os.path.join(data_dir,'yk_grpo_dev_completions.jsonl')
    dev_dataset = load_dataset('json',data_files=write_path)['train']
    dev_dataset = dev_dataset.select(range(5)) # 选择子集进行测试
    GRPO_formater = GRPO_Formater()
    dev_dataset = dev_dataset.map(score_process, num_proc=1,load_from_cache_file=False)
    model_type = 'opus'
    model_name = 'anthropic/claude-sonnet-4' if model_type == 'sonnet' else 'anthropic/claude-opus-4.1'

    _get_score_from_claude = partial(get_prompt_score, model=model_name, tokenizer=None, isrouter_key=True, enable_thinking=False, score_batch=4, isstop=True,handle_key='messages')
    dev_dataset = dev_dataset.map(_get_score_from_claude, num_proc=1,load_from_cache_file=False)

    dev_dataset.to_json(os.path.join(data_dir,'yk_grpo_dev_scores.jsonl'),lines=True,orient='records',force_ascii=False)



    ### 使用transformers库的示例输出
    # model = AutoModelForCausalLM.from_pretrained('../save_models/sft', trust_remote_code=True, device_map='auto', torch_dtype='auto')
    # tokenizer = AutoTokenizer.from_pretrained('../save_models/sft', trust_remote_code=True)
    # if tokenizer.pad_token is None:
    #     tokenizer.pad_token = tokenizer.eos_token
    # example_message = dev_dataset['prompt'][0]
    # example_message = tokenizer.apply_chat_template(example_message, add_generation_prompt=True, system_first=True,tokenize=False)
    # example_inputs = tokenizer(example_message, return_tensors='pt').to(model.device)
    # prompt_len = example_inputs['input_ids'].shape[1]
    # example_outputs = model.generate(**example_inputs, max_new_tokens=256, do_sample=True, top_p=0.7, temperature=0.95, eos_token_id=tokenizer.eos_token_id)
    # # 解码
    # example_completion = tokenizer.decode(example_outputs[0][prompt_len:], skip_special_tokens=True)