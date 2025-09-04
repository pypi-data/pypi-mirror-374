def output_format(score_batch):
    # json格式个数与completions长度有关
    format_str = '\n\n结果严格以JSON格式输出：{' + ', '.join([f'"{str(i+1)}": "分数, int型"' for i in range(score_batch)]) + '}'
    return format_str

def concat_generate_completions(completions):
    return '\n'.join([f'候选回答{i+1}. {completions[i]}' for i in range(len(completions))])

def concat_instructions(instructions,isreward=False):
    result = []
    counter = 1  # 全局编号计数器
    
    for instruction in instructions:
        # 分割前缀和内容
        if ':' in instruction:
            prefix, content = instruction.split(':', 1)
            prefix = prefix.strip() + ':'  # 保留冒号
        else:
            prefix = ''
            content = instruction
        # if isreward and '通用相关' in prefix:
        #     continue
        # 按换行符分割内容
        # if isreward:
        #     items = [item.strip() for item in content.split('\n') if item.strip() if not item.strip().endswith('(优先遵循)')]
        # else:
        if isreward:
            # items = [item.strip().replace('(优先遵循)','') + '(+1分)' for item in content.split('\n') if item.strip()]
            items = [item.strip().replace('(优先遵循)','') for item in content.split('\n') if item.strip()]
        else:
            items = [item.strip().replace('(优先遵循)','') for item in content.split('\n') if item.strip()]
        # 为每个项目编号并格式化
        for item in items:
            result.append(f'{counter}. {item}')
            counter += 1
    return '\n'.join(result)



def _system_template_rm(template_type):
    sys_template = '''你是一个具备专业的{_type}医疗知识的评分者，请根据**历史对话**、**回复策略**和**指令要求**对客服**候选回复集**逐个进行评分。
评分流程
### 第一步：策略一致性检查

如果候选回答与回复策略完全相悖，直接打0分，无需进行后续评分
如果候选回答与回复策略基本一致或部分符合，进入第二步详细评分

### 第二步：详细评分规则
基础分：0分（策略一致性通过后的基础分）
加分项目：

"要求"类指令：每完成一个要求类指令，加1分
"禁止"类指令：每个禁止类指令都不违反，加1分
"条件"类指令：
如果对话中出现了该情景且正确处理，加1分
如果对话中没有出现该情景，默认加1分

### 概念解释
回复策略类型：

**问诊**：在对话中进行医疗相关的问诊，解答患者问题的同时获取患者信息
**套电**：在对话中尝试用合适的理由获取患者的联系方式，进行后续跟进和服务

###指令类型识别：
**要求类**：明确要求执行某个动作的指令
**禁止类**：明确禁止做某件事的指令
**条件类**：条件性指令，针对某种情景的指令

### 评分示例
输入信息
**历史对话**：【轮次1】患者：眼睛有点看不清怎么办才能恢复<sep>眼睛有点模糊看的不太清，近几天，怎么回事啊
客服：视力模糊持续多久了呢?
【轮次2】患者：40
客服：除了模糊还有其他不舒服症状吗
【轮次3】患者：没有
客服：是看远看近的视力都模糊是吗？
【轮次4】患者：看东西有点头晕<sep>是的
客服：有胀痛的感觉吗
【轮次5】患者：有点温烧<sep>没有
回复策略：套电

**指令要求**：
成功获取联系方式后立即结束对话(+1分) [条件类]
患者年纪较大时，以并发症多为理由进行联系(+1分) [要求类]
以合理理由留联(+1分) [要求类]
禁止回答药物疗效、疗程等问题，禁止开处方，禁止介绍患者用药(+1分) [禁止类]
如果患者没有提及治疗、检查、价格、效果、疗程，则衔接回复话术也禁止提及(+1分) [条件类]

**候选回复**：
候选回答1：之前有过这种情况吗？
候选回答2：这种情况已经有多久了？
候选回答3：这种情况可能是由多种原因引起的，包括眼部问题或其他健康状况。为了更好地了解您的情况，能告诉我您的手机号码吗？我们可以安排一个专业的医生为您做进一步的咨询和指导。
候选回答4：您年龄比较大的情况下，如果出现视物异常的话可能是因为眼部疾病或者是全身性疾病影响导致。<sep>您目前是在哪个城市？

###评分过程
候选回答1评分：
策略检查：继续问诊，未尝试套电，违背策略，0分

候选回答2评分：
策略检查：继续问诊，未尝试套电，违背策略，0分

候选回答3评分：
策略检查：明确请求手机号码，符合套电策略，通过
基础分：0分
指令1（条件类）：未出现"成功获取联系方式"的情景，默认+1分
指令2（要求类）：未体现"年龄大+并发症"理由，+0分
指令3（要求类）：给出合理理由（安排医生咨询），+1分
指令4（禁止类）：未违反药物相关禁令，+1分
指令5（条件类）：患者确实未提及相关话题，回复也未涉及，+1分
总分：1+1+0+1+1+1=4分

候选回答4评分：
策略检查：提及年龄因素，但未直接要求联系方式，部分符合套电策略，通过
基础分：0分
指令1（条件类）：未出现"成功获取联系方式"的情景，默认+1分
指令2（要求类）：体现了"年龄大+并发症"理由，+1分
指令3（要求类）：未成功留联，只询问城市，+0分
指令4（禁止类）：未违反药物相关禁令，+1分
指令5（条件类）：患者确实未提及相关话题，回复也未涉及，+1分
总分：1+1+1+0+1+1=4分

**结果输出**：{{"1":0,"2":0,"3":4,"4":4}}
'''.format(_type='两性' if template_type == 'fck' else '眼科')
    return sys_template

def _user_template_rm(history,instruction_type,instructions,completions):
    user_template = '''**历史对话**：{history}
**回复策略**：{instruction_type}
**指令要求**：{instructions}
**候选回复**：{completions}
**结果输出**：
'''.format(history=history, instruction_type=instruction_type,instructions=instructions, completions=completions)
    return user_template


def template_rm(history, completions, instructions, template_type, instruction_type, score_batch):
    if template_type == 'fck':
        _type = '两性'
    elif template_type == 'erk':
        _type = '儿科'
    elif template_type == 'yk':
        _type = '眼科'
    else:
        raise 'eroor template_type' 
    return _system_template_rm(_type) + output_format(score_batch), _user_template_rm(history, instruction_type, instructions,completions)


def template_rm_single(history, completion, instructions, template_type, instruction_type):
    if template_type == 'fck':
        _type = '两性'
    elif template_type == 'erk':
        _type = '儿科'
    elif template_type == 'yk':
        _type = '眼科'
    else:
        raise 'eroor template_type' 
    system_prompt = _system_template_rm(_type).replace('**候选回复集**逐个','**候选回复**')
    if '评分示例' in system_prompt: # 确保不要截为空
        system_prompt = system_prompt[:system_prompt.find('### 评分示例')].strip()
    return _system_template_rm(_type).replace('**候选回复集**') , _user_template_rm(history, instruction_type, concat_instructions(instructions),completion)
