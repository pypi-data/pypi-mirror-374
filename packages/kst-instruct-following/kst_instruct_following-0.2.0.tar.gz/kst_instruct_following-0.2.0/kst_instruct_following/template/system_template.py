try:
    from kst_instruct_following.reward_template import concat_instructions
except:
    from reward_template import concat_instructions

def _system_template_rl(template_type,instruction_type):
    sys_template = '''你是一个具备专业的{_type}医疗知识的人工客服。请根据**回复策略**和**指令要求**，推进对话。

### 注意
在回复前，请严格遵循**回复策略**以及**指令要求**
**回复策略**：{instruction_type}
**当前指令**：
'''.format(_type='两性' if template_type == 'fck' else '眼科',instruction_type=instruction_type)
    return sys_template

def system_template_rl(instructions, template_type, instruction_type):
    return _system_template_rl(template_type,instruction_type) + concat_instructions(instructions)


def system_template_sft(template_type):
    if template_type == 'fck':
        _type = '两性'
    elif template_type == 'yk':
        _type = '眼科'
    elif template_type == 'erk':
        _type = '儿科'
    else:
        raise ValueError(f"Unknown template type: {template_type}")
    return '''你是一个具备专业的{_type}医疗知识的人工客服。'''.format(_type=_type)
