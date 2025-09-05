# 使用打分prompt进行更新completion部分
# 然后更新action
# 首先使用client生成4个回复 然后使用打分prompt批次打分
# 得到最好的作为chosen 3 4名的作为rejected
# 如果最好的有平分且大于2 则重新生成
from openai import OpenAI
from datasets import load_dataset
import argparse
import os
from kst_instruct_following.grpo_rewarder import GRPO_Rewarder, GRPO_Formater, get_prompt_score
from kst_instruct_following.processor import think_process,grpo_system_prompt_process,score_process
import json
import numpy as np
import random
from functools import partial

def generate_responses(client, messages, limit,enable_thinking=True,stop=[]):
    responses = []
    models = client.models.list()
    available_models = [model.id for model in models.data]
    model = available_models[0]
    try:
        if enable_thinking is not None:
            response = client.chat.completions.create(
                model=model, # 之前在run_inference.sh打开端口 设置的名字
                messages=messages,
                n=limit,
                extra_body={"chat_template_kwargs": {"enable_thinking": enable_thinking}},
                stop=stop
            )
        else: # 没有思考模式 不加think参数
            response = client.chat.completions.create(
                model=model, # 之前在run_inference.sh打开端口 设置的名字
                messages=messages,
                n=limit,
                stop=stop
            )
        # responses.append(response.choices[0].message.content)
        for i, choice in enumerate(response.choices):
            responses.append(choice.message.content)
    except Exception as e:
        responses = [str(e)]*limit
    return responses 

def get_score(client,sys_prompt,prompt):
    messages = [{'role': "system", 'content': sys_prompt}, {'role':"user", 'content': prompt}]
    scores = generate_responses(client, messages,1,stop=['}'])[0] # 生成一条(score)
    scores = scores[scores.find('</think>')+8:].strip() + '}'
    scores = json.loads(scores) # 解析json
    return scores

def check_score(scores):
    """
    检查分数字典并返回最大值和最小值的键
    输入格式: {"1": score1, "2": score2, ...}
    """
    # 找到最大值的索引
    max_key = max(scores, key=scores.get)
    
    # 找到最小值的索引
    min_key = min(scores, key=scores.get)
    
    # 检查条件：最大值 > 5 且 最大值索引 严格 > 最小值索引
    if scores[max_key] >= 3 and scores[max_key] > scores[min_key]:
        return True, max_key, min_key
    else:
        return False, None, None

def get_completion_and_check_score(example, get_completion_func, get_score_func, check_score_func,score_batch=4,try_count=4,mean_count=3):
    get_completion = partial(get_completion_func, model=model_name, tokenizer='', isrouter_key=False, enable_thinking=None, score_batch=score_batch, isstop=True, port=8890, G=4*try_count, isgenerate=True)
    get_score = partial(get_score_func, model=model_name, tokenizer=None, isrouter_key=False, enable_thinking=False, score_batch=score_batch, port=8891, isstop=True)
    example = get_completion(example)
    total_completions = example['completions'][:] # 不传递
    for i in range(try_count):
        example['completions'] = total_completions[i:i+4] # 一次性生成 每次取4个回复
        if i == 0:
            example = score_process(example)
        scores = np.zeros(4)
        # for j in range(mean_count):
        example = get_score(example)
        scores += example['score']
        scores = scores.tolist()
        # scores = (scores / mean_count).tolist()

        scores = {str(i+1): v for i, v in enumerate(scores)}
        isselect, max_index, min_index = check_score_func(scores)
        if isselect:

            example['max_index'] = int(max_index)
            example['min_index'] = int(min_index)
            example['valid'] = '1'
            return example
    example['max_index'] = -1
    example['min_index'] = -1
    example['valid'] = '0'
    return example

def _2grpo(example):

    # example['prompt'] = example['messages'][:-1] # 清理动作
    example['completion'] = [{'role':'assistant','content':'<think></think>' + example['completions'][example['max_index']-1]}] # 最后一条消息作为completion
    return example
def _2dpo(example):
    example['chosen'] = [{'role':'assistant','content':'<think></think>' + example['completions'][example['max_index']-1]}] # 最后一条消息作为completion
    example['rejected'] = [{'role':'assistant','content':'<think></think>' + example['completions'][example['min_index']-1]}] # 最后一条消息作为completion
    return example
def _2sft(example):
    completion = [{'role':'assistant','content':'<think></think>' + example['completions'][example['max_index']-1]}]
    example['messages'] = example['prompt'] + completion # 替换最后一条消息
    return example

if __name__ == '__main__':
    # 基于清洗 + 扩充后的grpo dataset 构造dpo数据（而不是sft数据）
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_type',default='dev',type=str)
    department = ['yk']
    # department = ['yk','fck','erk']

    # data_dir = '../dataset/yk/grpo'
    args = parser.parse_args()
    for _type in ['train']:
        handle_dataset = load_dataset('json',data_files= [f'../../dataset/{depart}/grpo/{depart}_grpo_{_type}_augument.jsonl' for depart in department])['train']
    

        # 得到的是completion的结果
        # handle_dataset = handle_dataset.select(range(32))
        model_name = 'Qwen3-8B' 
        ### 获取sft_unfol回复 -- 8890接口
        

        handle_dataset = handle_dataset.map(think_process, num_proc=1,load_from_cache_file=False) # 改为think格式

        handle_dataset = handle_dataset.map(grpo_system_prompt_process,num_proc=1) # 添加grpo的系统提示
        _get_model_completion = partial(get_prompt_score, model=model_name, tokenizer='', isrouter_key=False, enable_thinking=None, score_batch=4, isstop=True, port=8890, G=4, isgenerate=True)
        _get_score = partial(get_prompt_score, model=model_name, tokenizer=None, isrouter_key=True, enable_thinking=None, score_batch=4, port=8891, isstop=True, handle_key='messages')
        process_fun = partial(get_completion_and_check_score, get_completion_func=_get_model_completion,get_score_func=_get_score, check_score_func=check_score)
        # handle_dataset = handle_dataset.map(_get_model_completion, num_proc=8, load_from_cache_file=False)
        # handle_dataset = handle_dataset.map(score_process, num_proc=1, load_from_cache_file=False) # 添加一个message 的key用于打分

        ### 获取分数 -- 8891接口
        model_name = 'Qwen3-8B'
        
        # 再在外面包裹一个打分的函数

        handle_dataset = handle_dataset.map(process_fun, num_proc=32, load_from_cache_file=False) # 得到高分 低分index
        # 得到了completion和score的结果
        # 然后筛选好的completion作为SFT？不好的completion作为DPO的rejected
        # 得到好的index和不好的index即可？
        # 然后基于index写入SFT GRPO DPO -- 都作为raw？
        handle_dataset = handle_dataset.filter(lambda x:x['valid'] == '1')
        sft_dataset = handle_dataset.map(_2sft, num_proc=4, load_from_cache_file=False,remove_columns=['prompt','completion','max_index','min_index','score','think'])
        sft_dataset = sft_dataset.select_columns(['messages','department','instructions','instruction_type'])
        grpo_dataset = handle_dataset.map(_2grpo, num_proc=4, load_from_cache_file=False,remove_columns=['max_index','min_index','score','think'])
        grpo_dataset = grpo_dataset.select_columns(['prompt','completion','department','instructions','instruction_type'])
        dpo_dataset = handle_dataset.map(_2dpo, num_proc=4, load_from_cache_file=False,remove_columns=['messages','completion','max_index','min_index','score','think'])
        dpo_dataset = dpo_dataset.select_columns(['prompt','chosen','rejected','department','instructions','instruction_type'])
        sft_dataset.to_json(f'../../dataset/yk/sft/yk_sft_{_type}_if.jsonl',lines=True,force_ascii=False)
        grpo_dataset.to_json(f'../../dataset/yk/grpo/yk_grpo_{_type}_if.jsonl',lines=True,force_ascii=False)
        dpo_dataset.to_json(f'../../dataset/yk/dpo/yk_dpo_{_type}_if.jsonl',lines=True,force_ascii=False)

    
