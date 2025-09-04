from openai import OpenAI
import numpy as np
import re
import json
from instruct_following_project.src.template.reward_template import template_rm, output_format, concat_generate_completions, concat_instructions
from datasets import Dataset
import itertools
from functools import partial
from transformers import AutoTokenizer
from instruct_following_project.src.vllm_functions import get_prompt_score

from instruct_following_project.src.processor import dialogue_formater
class GRPO_Rewarder():
    def __init__(self,model,isrouter_key,format_cls,training_args,enable_thinking=False,isstop=True,port=8892,model_path = '/data1/public/Qwen/Qwen3/Qwen3-32B'):
        self.isrouter_key=isrouter_key
        self.model = model if self.isrouter_key else model_path
        self.format_cls = format_cls
        self.enable_thinking = enable_thinking
        # self.score_batch = training_args.num_generations # 与生成的一致
        self.score_batch = 4 # 以4个为一组，建议采样数G是score_batch的倍数
        self.isstop = isstop,
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        # self.num_proc = int(32 // self.score_batch) if int(32 // self.score_batch) <= 0 else 8
        self.num_proc = int(32 // self.score_batch)
        self.port = port
    def _get_reward_prompt(self,prompts,completions,instructions,instructions_type,department):
        '''
        处理流程说明：
        1. 数据分组处理
        - 以score_batch为分组大小，从不重复的prompts和instructions中采样
        - 确保每组包含唯一的提示词和指令组合
        2. 对话格式转换
        - 将prompts转换为标准历史对话格式：
            【轮次1】患者：xxx\n医生：xxx\n【轮次2】患者：xxx\n医生：xxx\n...
        3. 候选回复合并
        - 按score_batch分组合并completions：
            候选回复1：c1\n候选回复2：c2\n候选回复3：c3\n候选回复4：c4\n
        4. 指令整合
        - 合并instructions为编号列表格式：
            1. i11\n2. i12\n3. i13\n4. i14\n5. i15\n
        5. 构造模型输入
        - 系统提示词(sys_prompt)：定义评分角色、评分标准和输出格式要求
        - 用户提示词(user_prompt)：包含：
            * 历史对话内容
            * 当前指令列表  
            * 候选回复集合
            * 得分输出指示
        6. 输出结果
        - 返回处理后的历史对话文本
        - 返回拼接后的指令字段
        - 返回用于大模型打分的messages_list（包含system和user角色消息）

        注：每条指令i1包含五个子指令项，instruction_type为问诊或套电类型，department为当前数据科室名称
        '''

        completions = [completion[0]['content'] for completion in completions] # list中提取str
        ori_prompts = prompts.copy() # 备份原始prompts
        history_prompts = [dialogue_formater(prompt) for prompt in prompts] # 输入为content_list -- 输出为历史对话
        # 按score_batch分组
        history_prompts = [history_prompts[i] for i in range(0,len(history_prompts),self.score_batch)]
        instructions = [concat_instructions(instructions[i],isreward=True) for i in range(0,len(instructions),self.score_batch)] # 只打分轮次指定的instruction，all的不打分
        completions = [concat_generate_completions(completions[i:i+self.score_batch]) for i in range(0,len(completions),self.score_batch)]
        departments = [department[i] for i in range(0,len(department),self.score_batch)]
        instruction_type = [instructions_type[i] for i in range(0,len(instructions_type),self.score_batch)] # 只打分轮次指定的instruction_type，all的不打分
        pairs = [template_rm(history_prompt,completion,instruction,department,_instruction_type,self.score_batch) for history_prompt,completion,instruction,department,_instruction_type in zip(history_prompts,completions,instructions,departments,instruction_type)]

        sys_prompts, prompts = zip(*pairs) # 得到的是当前batch的按G分组的打分template
        messages_list = [[{'role':"system", 'content': sys_prompts[i]},{'role':"user", 'content': prompts[i]}] for i in range(len(prompts))] # 当前batch的要打分的所有messages
        return history_prompts,instructions,messages_list

    def _get_format_score(self,completions):
        completions = [c[0]['content'] for c in completions]
        return self.format_cls.reward_func_format(completions) # 格式化打分
    
    def get_batch_score(self,prompts,completions,instructions,instruction_type,department,is_log=True):
        '''
        输入的变量名与输入数据集的key一致
        通过大模型评分以及格式评分加权，得到一个batch的分数
        '''
        user_content = [prompt[-1]['content'] for prompt in prompts]
        instruction_content = [''.join(instruction).replace('\n','').replace('\t','') for instruction in instructions]
        assistant_content = [completion[-1]['content'] for completion in completions]
        history_content,concated_instructions,message_list = self._get_reward_prompt(prompts,completions,instructions,instruction_type,department)
        format_scores = self._get_format_score(completions)
        # 把message_list改为Dataset类 然后利用process的多进程代替并行推理
        data_dict = {
            'messages':[message for message in message_list]
        }
        message_dataset = Dataset.from_dict(data_dict)
        _get_prompt_score = partial(get_prompt_score, model=self.model, tokenizer=self.tokenizer, isrouter_key=self.isrouter_key, enable_thinking=self.enable_thinking, score_batch=self.score_batch, isstop=self.isstop,port=self.port)
        messages_dataset = message_dataset.map(_get_prompt_score, batched=False, num_proc=self.num_proc)
        # messages_dataset = message_dataset.map(_get_batch_score, batched=False, num_proc=1)
        prompt_scores = np.array(list(itertools.chain(*messages_dataset['score'])))
        think_strs = messages_dataset['think']
        # prompt_scores = self._get_batch_score(message_list, try_counts=try_counts, enable_thinking=enable_thinking, isstop=isstop)
        # 归一化
        # 当然 满足更多的 分数会更高
        # prompt_scores = 
        if is_log:
            self.write_generations(history_content, concated_instructions, assistant_content, think_strs, prompt_scores, format_scores)
            return (0.7 * prompt_scores / 5.0) + (0.3 * format_scores / 14.0) # 归一化后加权
        else:
            return message_dataset # 如果不是is_log形式 则返回整个dataset 用于非训练模式

    def write_generations(self, ori_prompts, instructions, completions, think_strs, prompt_scores, format_scores):
        try:
            with open('../logs/grpo_logs.log', 'a', encoding='utf-8') as f:
                # 确保所有数组长度一致或成比例
                assert len(ori_prompts) * self.score_batch == len(completions), \
                    f"Length mismatch: ori_prompts({len(ori_prompts)}), completions({len(completions)}), score_batch({self.score_batch})"
                
                for i in range(len(ori_prompts)):
                    ori_prompts[i] = ori_prompts[i].replace('\n','')
                    instructions[i] = instructions[i].replace('\n','')
                    think_strs[i] = think_strs[i].replace('\n','')
                    f.write(f"User_prompt: {ori_prompts[i]}\n")
                    f.write(f"Instruction: {instructions[i]}\n")
                    f.write(f"Reward_thinking: {think_strs[i]}\n")
                    
                    # 写入对应的score_batch个completion和score
                    for j in range(self.score_batch):
                        idx = i * self.score_batch + j
                        if idx < len(completions):
                            completion = completions[idx]
                            prompt_base_score = prompt_scores[idx]
                            format_base_score = format_scores[idx]
                            
                            f.write(
                                f"Completion: {completion}\n"
                                f"prompt_base_score: {prompt_base_score:.2f}\t"
                                f"format_base_score: {format_base_score:.2f}\n\n"
                            )
                    f.write("*"*20 + '\n')
        except Exception as e:
            print(e)


class GRPO_Formater():
    def __init__(self):
        pass

    def safe_reward_func(self,reward_func, *args, default_value=None):
        """安全执行 reward_func，出错时返回默认值"""
        try:
            return reward_func(*args)
        except Exception as e:
            print(f"Error in {reward_func.__name__}: {e}")
            return default_value if default_value is not None else np.zeros(len(args[0]), dtype=float)
    
    def reward_func_format(self, completions): 
        # 值域为[0,12]
        rewards_1 = self.safe_reward_func(self.reward_func_format_english, completions) # 英文单词
        rewards_2 = self.safe_reward_func(self.reward_func_format_special_char, completions) # 特殊字符
        rewards_3 = self.safe_reward_func(self.reward_func_format_sep, completions) # <sep>符号
        rewards_4 = self.safe_reward_func(self.reward_func_open_question_detailed, completions) # 开放性问诊
        rewards_5 = self.safe_reward_func(self.reward_func_format_comma, completions) # 逗号在一句话的个数
        rewards_6 = self.safe_reward_func(self.reward_func_obvious_ai, completions) # 明显AI特征
        rewards_7 = self.safe_reward_func(self.reward_func_style, completions) # 语气风格
        rewards = rewards_1 + rewards_2 + rewards_3  + rewards_4 + rewards_5 + rewards_6 + rewards_7
        return rewards

    def clean_text(self,completion):
        return completion.replace('<sep>', '').replace('\n', '').replace('\t', '',).replace(' ','')
        
    def reward_func_format_english(self,completions):
        import re
        # 仅匹配非中文、非中文标点的字符（排除空格）
        # pattern = re.compile(r'[^\u4e00-\u9fff\u3000-\u303f\s]')
        pattern = re.compile(r'[^\u4e00-\u9fff\u3000-\u303fA-Z0-9\s.,;:!?_@#$%^&*+=<>|`~，。；：！？''""（）【】｛｝、—…～]')
        # pattern = re.compile(r'[^\u4e00-\u9fff\u3000-\u303fA-Z0-9\s]')
        # pattern = re.compile(r'^[\u4e00-\u9fff\u3000-\u303fA-Z0-9\s\“”‘’，,。.；？！￥……《》（）：、`\n\r\t]*$')
        rewards = []
        for completion in completions:
            if '微信' in completion:
                rewards.append(2.0)
            else:
                illegal_chars = pattern.findall(self.clean_text(completion))
                penalty = 0.5 * len(illegal_chars)
                rewards.append(max(0, 2.0 - penalty))
        
        return np.array(rewards)

    def reward_func_format_special_char(self,completions):
        rewards = np.array([
            2.0 if '\n' not in completion and '\t' not in completion 
            else max(0, 2.0 - 0.2 * (completion.count('\n') + completion.count('\t')))
            for completion in completions
        ])
        return rewards

    def reward_func_format_sep(self,completions):
        rewards = np.array([
            2.0 if completion.count('<sep>') <= 2 
            else max(0, 2.0 - 0.5 * (completion.count('<sep>') - 2))
            for completion in completions
        ])
        return rewards

    def reward_func_format_comma(self,completions):
        """
        奖励逗号使用较少的文本（按<sep>分块后的平均逗号数量计算）
        规则：
        1. 以2.0为基准奖励
        2. 按分块后的平均逗号数量线性惩罚（每多一个逗号扣0.2分）
        3. 最低奖励为0.0（避免负值）
        """
        rewards = []
        for completion in completions:
            sentences = [s for s in completion.split('<sep>') if s.strip()]  # 过滤空分块
            if not sentences:  # 无有效分块时给基准奖励
                rewards.append(2.0)
                continue
                
            total_commas = sum(s.count('，') for s in sentences)
            avg_commas = total_commas / len(sentences)
            rewards.append(max(2.0 - 0.2 * avg_commas, 0.0))  # 平滑惩罚
            
        return np.array(rewards)

    ### 避免开放性问诊 -- 思路来自claude
    def reward_func_open_question_detailed(self,completions):
        """
        更详细的避免开放性问诊奖励函数
        可以区分不同严重程度的开放性问诊
        """
        # 严重的开放性问诊模式（更通用、更开放）
        import re
        severe_open_pattern = re.compile(
            r"(什么|哪些|怎么|哪里|哪种).{0,5}(不舒服|症状|情况|问题).{0,5}(呢|吗|？)|"
            r"还有其他.{0,5}(症状|问题|情况)|"
            r"目前.{0,5}什么情况|"
            r"咨询什么病情|"
            r"想了解哪方面"
        )
        # 中等的开放性问诊模式
        moderate_open_pattern = re.compile(
            r"有这样的情况吗|"
            r"其他的症状表现吗|"
            r"上述症状您|"
            r"以上症状有哪些|"
            r"这些情况有吗|"
            r"症状都?有吗"
        )
        # 轻微的开放性问诊模式
        mild_open_pattern = re.compile(
            r"目前.{0,8}(情况|症状|表现)|"
            r"大致了解|"
            r"描述.{0,4}情况|"
            r"了解下.{0,5}情况"
        )
        rewards = []
        for completion in completions:
            if severe_open_pattern.search(completion):
                rewards.append(0.0)    # 严重开放性问诊，重度负奖励
            elif moderate_open_pattern.search(completion):
                rewards.append(0.5)    # 中等开放性问诊，中度负奖励
            elif mild_open_pattern.search(completion):
                rewards.append(1.0)    # 轻微开放性问诊，轻度负奖励
            else:
                rewards.append(2.0)     # 没有开放性问诊，中性奖励
        return np.array(rewards)

    def reward_func_obvious_ai(self,completions):
        import re
        
        # 明显AI特征词汇列表
        ai_keywords = ['用户', 'Qwen', '通义','千问','思考', '以下', '助手', '作为', '根据您的', '很抱歉', '我无法', '我建议']
        
        # 分点回答的正则模式 (如 "1." "2." 等)
        numbered_pattern = re.compile(r'\d+\.')
        
        rewards = []
        for completion in completions:
            penalty_count = 0
            
            # 统计关键词出现次数
            for keyword in ai_keywords:
                penalty_count += completion.count(keyword)
            
            # 统计分点回答模式
            penalty_count += len(numbered_pattern.findall(completion))
            
            # 基础奖励1.0，按出现次数惩罚
            reward = max(2.0 - penalty_count * 1.0, 0)
            rewards.append(reward)
        
        return np.array(rewards)

    def reward_func_style(self, completions):
        cheerful_words = ['呀', '哈', '嘛', '咯', '呐']
        emoticons = ['~', '^^', '^_^']
        
        rewards = []
        for completion in completions:
            penalty = 0
            
            for word in cheerful_words:
                penalty += completion.count(word) * 0.5
            
            for emoticon in emoticons:
                penalty += completion.count(emoticon) * 0.5
            
            reward = max(2.0 - penalty, 0.0)
            rewards.append(reward)
        
        return np.array(rewards)
