from openai import OpenAI
import json
import numpy as np
import pandas as pd
import re
# from instruct_following_project.src.processor import think_process
# 外部函数，避免多进程序列化client
# 避免循环import
def think_process(example,enable_thinking,handle_key):
    _key = handle_key
    for i, content in enumerate(example[_key]):
        if content['role'] == 'user' and not example[_key][i]['content'].endswith('/think') and not example[_key][i]['content'].endswith('/no_think'):
            example[_key][i]['content'] = example[_key][i]['content'] + '/think' if enable_thinking else example[_key][i]['content'] + '/no_think'
        elif content['role'] == 'assistant' and not example[_key][i]['content'].startswith('<think>'):
            # example[_key][i]['content'] = '<think></think>' + example[_key][i]['content']
            example[_key][i]['content'] = '<think></think>' + example[_key][i]['content']
    return example

def get_prompt_score(example, model, tokenizer, isrouter_key = True, enable_thinking=None, score_batch=2, isstop=True, port=8892, G=1, isgenerate=False, handle_key=None):
    '''
    Args:
    example: 输入的示例数据
    model: 使用的模型
    tokenizer: 分词器
    isrouter_key: 是否为OpenRouter的API密钥，默认为True
    enable_thinking: 是否启用思考过程（仅适用于Qwen3模型，其他模型请设为None）
    score_batch: 打分模式下生成的候选结果数量，默认为2
    isstop: 打分模式下是否启用截断，默认为True
    port: 服务端口号，默认为8892
    G: 生成参数，控制生成多样性，默认为1
    isgenerate: 运行模式选择，False为打分模式，True为生成模式
    handle_key: 特殊处理密钥，默认为None

    Returns:
        根据模式返回评分结果或生成文本
        
    Note:
        - 打分模式：评估提示词质量并返回评分
        - 生成模式：基于提示词生成文本结果
    """
    # 初始化错误分数
    '''

    if isrouter_key or 'Qwen3' not in model:
        enable_thinking=None # 置为None 不适用template
    if not handle_key: # 默认用第一个
        handle_key = list(example.keys())[0]
    
    example = think_process(example,enable_thinking,handle_key) if enable_thinking is not None else example # 如果启用思考过程则处理一下example
    messages = example[handle_key]

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1" if isrouter_key else f'http://localhost:{port}/v1',
        api_key="" if isrouter_key else "monkeywu",  # 密钥
    )
    if not isrouter_key:
        models = client.models.list()
        available_models = [model.id for model in models.data]
        model = available_models[0] if available_models else None # 更新为自己的model

    error_score = np.zeros(score_batch, dtype=float)
    stop_words = ['}'] if isstop else []
    if enable_thinking: # 如果为True
        end_think_token = '</think>'
    try:
        responses = client.chat.completions.create(
            model=model,
            messages=messages,
            extra_body={"chat_template_kwargs": {"enable_thinking": enable_thinking}},
            n=G, # 生成的个数 如果是打分则生成一个，如果是其他则指定生成
            temperature=0.2 if not isgenerate else 1.0,
            top_p=0.9 if not isgenerate else 1.0,
            max_completion_tokens=40 if not isgenerate and not enable_thinking else 1024, # 对api调用的打分回复强制截断
            stop=stop_words if not isgenerate else None,
            logit_bias = {token_id:5 for token_id in tokenizer.encode(end_think_token)} if enable_thinking else None
        )
        if isgenerate:
            completions = []
            for i, choice in enumerate(responses.choices):
                clean_response = re.sub(r'<think>.*?</think>\n\n', '', choice.message.content,flags=re.DOTALL).strip() # 清除think字段
                completions.append(clean_response)
            example['completions'] = completions
            return example
        else:
            raw_responses = responses.choices[0].message.content

        try:
            # responses = raw_responses + stop_words[0] if isstop else raw_responses # 如果有stop word的情况则添加'}'
            think_str_match = re.search(r'<think>.*?</think>\n\n', raw_responses, flags=re.DOTALL)
            if think_str_match:
                think_str = think_str_match.group(0).replace('<think>', '').replace('</think>', '').replace('\n','').strip()
            else:
                think_str = '' if enable_thinking else raw_responses # 直接返回输出结果
                if enable_thinking:
                    print('not found the end think token')
                # return {'score':error_score,'think':responses if enable_thinking else ''} # 直接结束思考
            clean_response = re.sub(r'<think>.*?</think>\n\n', '', raw_responses,flags=re.DOTALL).strip() # 清除think字段
            if isstop:
                clean_response += stop_words[0]
            clean_response = clean_response[:clean_response.find('}')+1].replace('\n','').replace('```json','').replace('[','').replace(']','').replace(' ','')
            clean_response = clean_response[clean_response.find('{'):]
            score = json.loads(clean_response)
            
            # 验证分数完整性
            current_batch = []
            for j in range(1, score_batch + 1):
                key = str(j)
                if key not in score:
                    raise ValueError(f"Missing score for candidate {key}")
                current_batch.append(float(int(score[key])))
            example['score'] = np.array(current_batch, dtype=float)
            example['think'] = think_str if enable_thinking else '' # 如果启用思考则返回思考内容
            return example
            
        except Exception as e:
            print(f"Response parsing failed: {raw_responses[:100]}... | Error: {str(e)}")
            example['score'] = error_score
            example['think'] = think_str if enable_thinking else ''
            return example
            
    except Exception as e:
        print(f"API call failed: {str(e)}")
        if isgenerate:
            example['completions'] = []
            return example
        else:
            example['score'] = error_score
            example['think'] = think_str if enable_thinking else ''
            return example
        
        

def first_turn_cleaner(messages,client,model,enable_thinking=False,G=1):
    try:
        responses = client.chat.completions.create(
            model=model,
            messages=messages,
            extra_body={"chat_template_kwargs": {"enable_thinking": enable_thinking}},
            n=G, # 生成的个数 
            temperature=0.2,
            max_completion_tokens=1024
        )
        raw_responses = responses.choices[0].message.content
        think_str_match = re.search(r'<think>.*?</think>\n\n', raw_responses, flags=re.DOTALL)
        if think_str_match:
            think_str = think_str_match.group(0).replace('<think>', '').replace('</think>', '').replace('\n','').strip()
        else:
            think_str = '' if enable_thinking else raw_responses # 直接返回输出结果
        clean_response = re.sub(r'<think>.*?</think>\n\n', '', raw_responses,flags=re.DOTALL).strip() # 清除think字段
    except:
        clean_response = ''
    return clean_response
        