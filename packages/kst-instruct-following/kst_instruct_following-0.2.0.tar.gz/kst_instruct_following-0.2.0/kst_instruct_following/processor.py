from kst_instruct_following.template.reward_template import concat_generate_completions, concat_instructions, template_rm_single, template_rm
from kst_instruct_following.template import system_template
from kst_instruct_following.template import first_turn_template
from kst_instruct_following.vllm_functions import first_turn_cleaner
from functools import partial
from openai import OpenAI
from datasets import Dataset
import json
def score_process(example): # 处理打分的过程
    instructions = example['instructions']
    prompt = example['prompt']
    completions = example['completions']
    instruction_type = example['instruction_type']
    history_dialog = dialogue_formater(prompt)
    _completions = concat_generate_completions(completions)
    _instructions = concat_instructions(instructions,isreward=True)
    system_prompt, user_prompt = template_rm(history_dialog, _completions, _instructions, template_type='yk', instruction_type=instruction_type,score_batch=len(completions)) # 仅处理眼科数据
    messages = [{'role':'system','content':system_prompt},{'role':'user','content':user_prompt}]
    example['messages'] = messages
    return example
    

def grpo_system_prompt_process(example):
    if example['prompt'][0]['role'] == 'system':
        # sys_prompt = system_template._system_template(example['department']) + system_template.concat_instructions(example['instructions'])
        sys_prompt = system_template.system_template_rl(example['instructions'],example['department'],example['instruction_type'])
        sys_content = [{'role':'system','content':sys_prompt}]
        example['prompt'][0]['content'] = sys_prompt
    else:
        # sys_prompt = system_template._system_template(example['department']) + system_template.concat_instructions(example['instructions'])
        sys_prompt = system_template.system_template_rl(example['instructions'],example['department'],example['instruction_type'])
        sys_content = [{'role':'system','content':sys_prompt}]
        example['prompt'] = sys_content + example['prompt']
    return example

def sft_system_prompt_process(example):
    if example['messages'][0]['role'] == 'system':
        # sys_prompt = system_template._system_template(example['department']) + system_template.concat_instructions(example['instructions'])
        sys_prompt = system_template.system_template_sft(example['department'])
        sys_content = [{'role':'system','content':sys_prompt}]
        example['messages'][0]['content'] = sys_prompt
    else:
        # sys_prompt = system_template._system_template(example['department']) + system_template.concat_instructions(example['instructions'])
        sys_prompt = system_template.system_template_sft(example['department'])
        sys_content = [{'role':'system','content':sys_prompt}]
        example['messages'] = sys_content + example['messages']
    return example


def rm_system_prompt_process(example):
    history = dialogue_formater(example['prompt'][1:])
    sys_prompt,user_prompt = system_template.template_rm(history=history,instructions=example['instructions'], template_type=example['department'], instruction_type=example['instruction_type'])
    sys_content = [{'role':'system','content':sys_prompt}]
    user_content = [{'role':'user','content':user_prompt}]
    example['messages'] = sys_content + user_content
    return example

def think_process(example,enable_thinking=False):
    _key = list(example.keys())[0]
    for i, content in enumerate(example[_key]):
        if content['role'] == 'user' and not example[_key][i]['content'].endswith('/think') and not example[_key][i]['content'].endswith('/no_think'):
            example[_key][i]['content'] = example[_key][i]['content'] + '/think' if enable_thinking else example[_key][i]['content'] + '/no_think'
        elif content['role'] == 'assistant' and not example[_key][i]['content'].startswith('<think>'):
            # example[_key][i]['content'] = '<think></think>' + example[_key][i]['content']
            example[_key][i]['content'] = '<think></think>' + example[_key][i]['content']
    return example

def rewrite_clean_process(example): # 针对改写的进行清洗
    _key = 'messages'
    handle_content = example[_key][2]['content']

    cut_after_prefixes = ['注：', '改写说明：', '解析：', '解释']
    # 需要截断前面的前缀（保留后面的内容）
    cut_before_prefixes = ['改写：', '改写回复：']

    # 先处理截断后面的情况
    for prefix in cut_after_prefixes:
        if prefix in handle_content:
            handle_content = handle_content.split(prefix)[0]  # 取前缀之前的部分

    for prefix in cut_before_prefixes:
        if prefix in handle_content:
            handle_content = prefix.join(handle_content.split(prefix)[1:])  # 取前缀之后的部分

    handle_content = (
        handle_content
        .replace('**', '')
        .replace('\n', '')
        .replace('（', '')
        .replace('(', '')
        .replace(' ', '')
        .strip()
    )


    if handle_content.startswith('sep>'):
        handle_content = handle_content[:4]
    # 如果还存在改写 则valid = 0
    # 否则valid = 1
    # 更新内容
    if '改写' in handle_content:
        example['valid'] = '0'
    else:
        example['valid'] = '1'
    example[_key][2]['content'] = handle_content
    return example


def first_turn_process(example,port,enable_thinking=False):
    client = OpenAI(
        base_url=f"http://localhost:{port}/v1",
        api_key="monkeywu",  # 密钥
    )

    models = client.models.list()
    available_models = [model.id for model in models.data]
    model = available_models[0] if available_models else None # 更新为自己的model


    example = sft_system_prompt_process(example)
    # 构造改写template 然后对第一轮进行处理
    history_dialog = dialogue_formater(example['messages'][1:-1]) # 删除sys和最后一个assistant
    affix = '/think' if enable_thinking else '/no_think'
    system_prompt = first_turn_template.sys_template()
    user_prompt = first_turn_template.user_template(history_dialog)
    # user_prompt = user_prompt[:user_prompt.find('【轮次2】')]
    input_message = [{'role':'system','content':system_prompt},{'role':'user','content':user_prompt + affix}]
    try:
        response_content = first_turn_cleaner(input_message,client,model,enable_thinking=enable_thinking,G=1)
        if response_content != '':
            example['messages'][2]['content'] = response_content # 修改第一轮的回复
    except Exception as e:
        print(e)
    return example

def flatten_process(dataset): # 与其他的process不同 输入的应该是一整个dataset 而不是一个example
    def expand_completions(example):
        expanded_examples = []
        for i, (completion, score) in enumerate(zip(example['completions'], example['score'])):
            new_example = example.copy()
            new_example['completion'] = completion
            new_example['score'] = score
            new_example.pop('completions', None)
            new_example.pop('score',None)
            new_example.pop('messages',None)
            new_example.pop('think',None)
            expanded_examples.append(new_example)
        return expanded_examples

    expanded_data = []
    for example in dataset:
        expanded_data.extend(expand_completions(example))
    return Dataset.from_list(expanded_data)


def dialogue_formater(prompt):
    if isinstance(prompt,str):
        prompt = prompt.replace('<|im_start|>system\nYou are a helpful assistant.<|im_end|>', '') # 先移除system部分
        parts = prompt.split('<|im_start|>user\n')[1:] # 跳过第一个空元素
        formatted = []
        for i, part in enumerate(parts, 1):
            # 尝试分割用户和客服消息
            user_assistant = part.split('<|im_start|>assistant\n')
            
            # 提取用户消息
            user_msg = user_assistant[0].split('<|im_end|>')[0].strip()
            
            # 检查是否有客服回复
            if len(user_assistant) > 1:
                assistant_msg = user_assistant[1].split('<|im_end|>')[0].strip()
                formatted.append(f"【轮次{i}】患者：{user_msg}\n客服：{assistant_msg}\n")
            else:
                formatted.append(f"【轮次{i}】患者：{user_msg}")
        
        return '\n'.join(formatted)
    elif isinstance(prompt,list):
        # cluade -- 代码润色
        # 处理每条数据
        if len(prompt) == 0:
            return ""
        formatted = []
        content_list = prompt[1:] if len(prompt) > 1 and prompt[0]['role'] == 'system' else prompt # 去除system prompt的元素
        # 确保列表长度为奇数（最后一个元素必须是user）
        if len(content_list) % 2 == 0:
            # 如果是偶数长度，说明最后一个不是user，这不符合预期
            # 可以选择截断或者抛出异常
            content_list = content_list[:-1]  # 截断最后一个元素
        
        # 按user-assistant对处理，最后可能有单独的user
        turn_count = 1
        for i in range(0, len(content_list), 2):
            user_msg = content_list[i]['content'].strip()
            
            # 检查是否还有assistant回复
            if i + 1 < len(content_list):
                assistant_msg = content_list[i + 1]['content'].strip()
                formatted.append(f"【轮次{turn_count}】患者：{user_msg}\n客服：{assistant_msg}")
            else:
                # 最后一个user消息，没有assistant回复
                formatted.append(f"【轮次{turn_count}】患者：{user_msg}")
            
            turn_count += 1
        
        return ('\n'.join(formatted)).replace('<think>','').replace('</think>','').replace('/no_think','')