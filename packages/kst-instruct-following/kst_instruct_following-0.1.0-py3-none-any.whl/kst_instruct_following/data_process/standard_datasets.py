# 对眼科 妇产科的数据 标准化未没有systemprompt的sft grpo dpo数据
import json
import os
from datasets import load_dataset, concatenate_datasets
from datasets import Features, Sequence, Value, Dataset
import random
import re
from functools import partial
from Config import generate_config
from collections import OrderedDict
from instruct_following_project.src.grpo_rewarder import GRPO_Formater
try:
    from instruct_following_project.src.processor import first_turn_process, rewrite_clean_process
except:
    from processor import first_turn_process, rewrite_clean_process
class Standard_datasets():
    def __init__(self,department):
        self.data_dir = '../../dataset'
        self.department = department
        self.raw_dir = os.path.join(self.data_dir,department,'raw')
        self.sft_dir = os.path.join(self.data_dir,department,'sft')
        self.dpo_dir = os.path.join(self.data_dir,department,'dpo')
        self.grpo_dir = os.path.join(self.data_dir,department,'grpo')
        self.insturct_dict_file = os.path.join(self.data_dir,'instruction_cluster_dict.json')
        self.insturct_dict = self.load_instruct_dict()
        self.num_proc=64
    
    def filter_dataset(self,_raw_dataset,filter_func):
        raw_dataset = _raw_dataset.map(filter_func,load_from_cache_file=False,num_proc=1)
        raw_dataset = raw_dataset.filter(lambda x: x['valid'] == '1',load_from_cache_file=False).remove_columns(['valid'])   
        # raw_dataset = raw_dataset.remove_columns(['valid'])    

        return raw_dataset

    def first_turn_rewrite(self,dataset):
        _first_turn_process = partial(first_turn_process, port=8892, enable_thinking=True)
        # dataset = dataset.select(range(32))
        dataset = dataset.map(_first_turn_process,num_proc=self.num_proc,load_from_cache_file=False)
        # dataset = dataset.map(_first_turn_process,num_proc=1,load_from_cache_file=False)
        dataset = self.filter_dataset(dataset,self.prehandle_filter)
        return dataset

    


    def build_dataset(self,train_type,data_type,dataset_features=None,is_rewrite=False):
        # 然后后续再接着处理这些文件
        def sft_process(example):
            if example['messages'][0]['role'] == 'system': # 去除system prompt
                example['messages'] = example['messages'][1:]
            return example
        def grpo_process(example):
            if example['messages'][0]['role'] == 'system': # 去除system prompt
                example['messages'] = example['messages'][1:]
            example['prompt'] = example['messages'][:-1] # 清理动作
            example['completion'] = [example['messages'][-1]] # 最后一条消息作为completion
            return OrderedDict({
                'prompt': example['prompt'],
                'completion': example['completion'],
                'department': example['department']
            })
        def dpo_process(example):
            if example['messages'][0]['role'] == 'system':
                example['messages'] = example['messages'][1:]
            return OrderedDict({'chosen':example['messages'],'rejected':example['messages'],'department':self.department}) # 暂时chosen == rejected 后续grpo训好模型以后再调优

        

        rewrite_path = os.path.join(self.raw_dir,f'{self.department}_{data_type}_rewrite.jsonl')
        if os.path.exists(rewrite_path): # 如果已经重写
            print('already rewrite!!!')
            raw_dataset = load_dataset('json', data_files=rewrite_path)['train']
            # raw_dataset = raw_dataset.map(rewrite_clean_process, num_proc=1, load_from_cache_file=False) # 清理改写
            raw_dataset = self.filter_dataset(raw_dataset,rewrite_clean_process)
        else:
            _raw_dataset = load_dataset('json', data_files=os.path.join(self.raw_dir,f'{self.department}_{data_type}.jsonl'))['train']
            _raw_dataset = self.filter_dataset(_raw_dataset,self.prehandle_filter)
            if is_rewrite: # 如果没有重写 且需要重写
        
                # _raw_dataset = _raw_dataset.select(range(10))
                raw_dataset = self.first_turn_rewrite(_raw_dataset)
                raw_dataset = self.filter_dataset(raw_dataset,rewrite_clean_process)
                raw_dataset.to_json(rewrite_path,force_ascii=False)
                
            else: # 如果没有重写 且不需要重写
                raw_dataset = _raw_dataset
                raw_dataset = self.filter_dataset(raw_dataset,self.prehandle_filter)
                raw_dataset = self.filter_dataset(raw_dataset,rewrite_clean_process)

        
        if train_type == 'sft':
            dataset = raw_dataset.map(sft_process,num_proc=self.num_proc,load_from_cache_file=False)
        elif train_type == 'grpo':
            dataset = raw_dataset.map(grpo_process,num_proc=self.num_proc,load_from_cache_file=False,remove_columns='messages')
            dataset = dataset.select_columns(['prompt','completion','department']) # 只保留prompt和completion
        elif train_type == 'dpo':
            dataset = raw_dataset.map(dpo_process,num_proc=self.num_proc,load_from_cache_file=False,remove_columns='messages')
            dataset = dataset.select_columns(['chosen','rejected','department']) # 只保留chosen和rejected
        write_dir = os.path.join(self.data_dir,self.department,train_type)
        os.makedirs(write_dir, exist_ok=True)
        if dataset_features is not None:
            dataset = self.convert_dataset_schema(dataset, dataset_features)
        dataset.to_json(os.path.join(write_dir,f'{self.department}_{train_type}_{data_type}.jsonl'),force_ascii=False)
        print('finish_build_dataset',self.department,train_type,data_type)
        return dataset,dataset.features

    def clean_action(self,content_list):
        for i, content in enumerate(content_list):
            if content['role'] != 'user':
                completion = content_list[i]['content']
                completions_no_action = completion[completion.find(')')+1:] if completion.startswith('(') else completion
                content_list[i]['content'] = completions_no_action
        return content_list

    def prehandle_filter(self,example):
        example['messages'] = self.clean_action(example['messages']) # 清理动作
        example['department'] = self.department # 添加department
        if not example['messages']:
            example['valid'] = '0'
            return example
        content_list = example['messages'][1:] if example['messages'][0]['role'] == 'system' else example['messages']
        # 如果存在非法字符
        legal_pattern = re.compile(r'^[\u4e00-\u9fff\u3000-\u303fa-zA-Z0-9\s.,;:!?()[\]{}\'"“”‘’—–\-_=+*/\\|<>@#$%^&~`·，,。.；？！￥……《》<>;（）-：～‘’“”【】、`\n\r\t]*$')
        for content in content_list:
            if not legal_pattern.match(content['content']):
                # print(f"非法内容: {content['content']}")
                # print("非法字符:")
                # for char in content['content']:
                #     if not legal_pattern.match(char):
                #         print(f"'{char}' (Unicode: {ord(char):04x})")
                example['valid'] = '0'
                return example
        # 检查是否有明显的 < 和 > 字符（排除 <sep>）
        any_obvious_tag = any(['<' in content['content'].replace('<sep>', '') or '>' in content['content'].replace('<sep>', '') for content in content_list])
        
        # 如果有明显标签，则过滤掉
        if any_obvious_tag:
            example['valid'] = '0'
            return example
        # 检查是否存在连续且不超过8的限定字符子串
        pattern = re.compile(r'[A-Za-z0-9_]+')
        any_error_str = False
        
        for i, content in enumerate(content_list):
            matches = pattern.findall(content_list[i]['content'].replace('<sep>', ''))
            for match in matches:
                if len(match) <= 8 and content_list[i]['role'] == 'user':
                    # 如果是纯数字，则不满足条件
                    if re.match(r'^\d+$', match):
                        continue
                    # 如果是纯英文且为"ok"，则不满足条件
                    if re.match(r'^[A-Za-z]+$', match) and match.lower() == 'ok':
                        continue
                    # 其他情况（英文+数字，或纯英文但不是ok）满足条件
                    any_error_str = True
                    break
            if any_error_str:
                break
        if any_error_str:
            example['valid'] = '0'
            return example
        # 检查纯限定字符（超过8个）并替换
        pattern_full = re.compile(r'^[A-Za-z0-9_]+$')
            
        for i, content in enumerate(content_list):
            if pattern_full.match(content_list[i]['content']) and len(content_list[i]['content']) >= 8:
                # 检查是否为纯数字
                if re.match(r'^\d+$', content_list[i]['content']):
                    # 检查前一个content是否包含关键词
                    if i > 0 and ('手机' in content_list[i-1]['content'] or '电话' in content_list[i-1]['content']):
                        templates = ['我手机号为{}', '我手机号是{}', '加我,{}', '好的，{}', 'ok，我手机号{}']
                    else:
                        templates = ['我的微信是{}', '那你加我吧{}', '加我,{}', 'ok，我微信号{}']
                else:
                    # 不是纯数字
                    templates = ['我的微信是{}', '那你加我吧{}', '加我,{}', 'ok，我微信号{}']
                template = random.choice(templates)
                content_list[i]['content'] = template.format(content_list[i]['content'])
        example['messages'] =  [example['messages'][0]] + content_list
        example['valid'] = '1'
        return example


    def convert_dataset_schema(self, dataset, target_features):
        """将数据集转换为目标 schema"""
        def process_example(example):
            def _process_example(key):
                new_messages = []
                for msg in example[key]:
                    new_msg = {
                        'role': str(msg['role']),
                        'content': str(msg['content'])
                    }
                    new_messages.append(new_msg)
                return new_messages
            handle_keys = list(example.keys())
            for _key in handle_keys:
                if _key in ['messages', 'prompt', 'completion','chosen', 'rejected']:
                    example[_key] = _process_example(_key)
            # example['completion'] = _process_example('completion')
            return example
        processed_data = []
        for item in dataset:
            processed_item = process_example(item)
            processed_data.append(processed_item)
        # 创建新的数据集
        return Dataset.from_list(processed_data, features=target_features)
    
    def generate_dataset_with_instructions(self, train_type, data_type, rounds):
        read_path = os.path.join(self.data_dir,self.department,train_type,f'{self.department}_{train_type}_{data_type}.jsonl')
        dataset = load_dataset('json', data_files=read_path)['train']
        def _generate_datast_with_instructions(example):
            content_keys = list(example.keys())
            handle_key = content_keys[0] 
            turn = str(len(example[handle_key]) // 2) # 当前轮次
            rand = random.random()
            related_config = generate_config[str(turn)] if turn in generate_config else generate_config['other']
            values = list(related_config.values())
            # 查看落在哪个区间
            for i, value in enumerate(values):
                if rand <= value:
                    instruction_type = list(related_config.keys())[i]
                    break

            example['instructions'] = self.select_instructions(instruction_type,turn)
            example['instruction_type'] = instruction_type
            if '尝试获取患者联系方式' in example['instructions']:
                print('example:', example)
            return example
        dataset_tmp = dataset.select(range(len(dataset)))
        augmented_dataset = None 
        for round in range(rounds):
            sub_dataset = dataset_tmp.map(_generate_datast_with_instructions,load_from_cache_file=False,num_proc=self.num_proc)
            if augmented_dataset is None:
                augmented_dataset = sub_dataset
            else:
                # 随机的取生成的结果而不是全部 -- 至少50%
                # rand_part = random.random()
                # selcet_part = int(len(sub_dataset) * rand_part) if rand_part > 0.5 else int(len(sub_dataset) * (rand_part + 0.5))
                # sub_dataset = sub_dataset.select(range(selcet_part))
                augmented_dataset = concatenate_datasets([augmented_dataset, sub_dataset])
        write_dir = os.path.join(self.data_dir,self.department,train_type)
        augmented_dataset.to_json(os.path.join(write_dir,f'{self.department}_{train_type}_{data_type}_augument.jsonl'),force_ascii=False)
        return augmented_dataset
    def load_instruct_dict(self):
        with open(self.insturct_dict_file,'r') as f:
            instruction_dict = json.load(f)
        return instruction_dict
    
    def select_instructions(self,instruction_type,turn):
        def random_select_instructions_from_cluster(instruction_dict,_key,cluster_count=2,affix=''):
            related_rand_instructions = []
            related_turn_instructions_cluster = instruction_dict[_key]
            related_rand_cluster_index = random.sample(range(len(related_turn_instructions_cluster)),cluster_count)
            selected_clusters = [related_turn_instructions_cluster[idx] for idx in related_rand_cluster_index]
            # 随机抽取一条
            for cluster in selected_clusters:
                related_rand_instruction_index = random.sample(range(len(cluster)),1)
                related_rand_instruction = cluster[related_rand_instruction_index[0]]
                related_rand_instructions.append(related_rand_instruction + affix)
            if isinstance(related_rand_instructions,list): # 保证是list
                return related_rand_instructions
            else:
                return [related_rand_instructions]
        
        if instruction_type == '问诊':
            extra_instruction_dict = self.insturct_dict['问诊相关']
        elif instruction_type == '套电':
            extra_instruction_dict = self.insturct_dict['套电相关']
        else:
            # 随机选一个问诊或套电
            extra_instruction_dict = random.choice([self.insturct_dict['问诊相关'], self.insturct_dict['套电相关']])
        instructions_prompts = []

        # 先根据extra 和turn抽取turn的指令和all的指令
        # 再遍历通用相关
        # if extra_instruction_dict == {}:
        #     return instructions_prompts # 避免添加'无'这个key
        related_instructions_prompt = f'{instruction_type}相关: '
        rand_instructions = []
        if 'all' in extra_instruction_dict:
            related_rand_instructions = random_select_instructions_from_cluster(extra_instruction_dict,'all',cluster_count=2,affix='(优先遵循)')
            rand_instructions.extend(related_rand_instructions)
            related_instructions_prompt += '\n'.join(related_rand_instructions) 
            related_instructions_prompt += '\n' # 最后一个
        if turn in extra_instruction_dict: # 指定轮次的指令
            related_rand_instructions = random_select_instructions_from_cluster(extra_instruction_dict,turn,cluster_count=1)
            rand_instructions.extend(related_rand_instructions)
            related_instructions_prompt += '\n'.join(related_rand_instructions)
        elif 'other' in extra_instruction_dict: # 未指定轮次的指令
            related_rand_instructions = random_select_instructions_from_cluster(extra_instruction_dict,'other',cluster_count=1)
            rand_instructions.extend(related_rand_instructions)
            related_instructions_prompt += '\n'.join(related_rand_instructions)

        if instruction_type != '无':
            instructions_prompts.append(related_instructions_prompt)

        for key in ['通用相关']:
            related_rand_instructions = random_select_instructions_from_cluster(self.insturct_dict[key],'all',cluster_count=2)
            rand_instructions.extend(related_rand_instructions)
            related_instructions_prompt = f'{key}: ' + '\n'.join(related_rand_instructions)
            instructions_prompts.append(related_instructions_prompt)
        if len(rand_instructions) != 5:
            raise 'Error: Not enough instructions selected, expected 5 but got {}'.format(len(rand_instructions))
        return instructions_prompts
if __name__ == '__main__':
    # raw2sft 
    # raw2dpo
    # raw2grpo
    train_types = ['grpo','sft','dpo']
    data_types = ['dev','train']
    # data_types = ['dev'] 
    Yk_standard = Standard_datasets('yk')
    Fck_standard = Standard_datasets('fck')
    Erk_standard = Standard_datasets('erk')
    for train_type in train_types:
        for data_type in data_types:
            print('start build dataset:',train_type,data_type)
            yk_dataset, yk_dataset_features = Yk_standard.build_dataset(train_type,data_type,is_rewrite=True)
            fck_dataset, fck_dataset_features = Fck_standard.build_dataset(train_type,data_type,yk_dataset_features,is_rewrite=True)
            erk_dataset, erk_dataset_features = Erk_standard.build_dataset(train_type,data_type,yk_dataset_features,is_rewrite=True)
            # yk_dataset_with_instructions = Yk_standard.generate_dataset_with_instructions(train_type,data_type,rounds=1)
            fck_dataset_with_instructions = Fck_standard.generate_dataset_with_instructions(train_type,data_type,rounds=1)
            erk_dataset_with_instructions = Erk_standard.generate_dataset_with_instructions(train_type,data_type,rounds=1)
    