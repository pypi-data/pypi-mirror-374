## 指令跟随

医疗营销套电模型的目的是通过与患者在问诊的过程中建立信任，并在合理的时机索取患者联系方式，以期后续人工介入营销的机器人。

然而，目前的机器人指令跟随能力较差，包括符合人类偏好的通用指令以及不同需求方的特殊指令。提升指令跟随能力对机器人的套电成功率的提高具有很大的潜力，如：适应对话套路和流程、提高对话延续性、避免潜在纠纷风险等等。


### 建议服务器
192.168.1.67 [66服务器上可能由部分代码不是最新版]

#### 指令跟随项目
---
/data/daixl/RL_study/instruct_following_project

    -- dataset/ # 存放了儿科、眼科、妇产科的数据
    -- instruction_cluster_dict.json #存放从 约束_new.xlsx 转换的json格式
    -- logs/ # 保存vllm和grpo采样回复和打分
    -- output/ # 存放模型训练checkpoint
    -- save_models/ # 存放训练好的模型
    -- script/ # 存放训练脚本
    -- src/ # 存放主要代码
    -- data_process/
        -- Config.py # 为按轮次随机构造策略和指令
        -- instruction_constructor.py # 将 约束_new.xlsx 
            # 转换为instruction_cluster_dict.json
        -- standard_datasets.py # 通过原始数据生成sft dpo grpo的数据 
            # 以及带指令约束的数据
        -- instruction_follow_creator.py # 针对带指令约束的数据采样-打分
            # 对应的completion[还需要优化,因为并不是所有的回复都满足指令(脏数据)]
    -- template/ # 存放不同的prompt模板
    -- processor.py # 为不同的数据预处理函数
    -- sft_training.py 为sft训练代码
    -- grpo_training.py 为grpo训练代码
    -- grpo_rewarder.py 为Rewarder类
    -- vllm-functions.py 为Rewarder采样以及其他采样生成回复时的调用函数
    -- reward_model_trianing.py 为reward model 训练代码,未完善
    -- vllms/ #存放vllm接口脚本，
---
### 自动化测试
/data/daixl/RL_study/deployment

分别为妇产科以及眼科的自动化测试脚本, 自行修改structure_data.py下的Dialog类的dialog_to_str_dxl函数以修改模型输入

---
### 外部数据集
/data/daixl/RL_study/dataset

也等价于 

/data/public/data/Med_datasets/extra_format_datasets

### zhongpei记录

- 数据鼻祖（没有经过任何处理的数据）
    - /data3/zhongp/instruct_following_project/dataset/yk/raw/yk_train.jsonl
- 数据流程：
    1. yk_train.jsonl
    2. yk_train_rewrite.jsonl：由yk_train.jsonl改写而来
    3. yk_sft_train_if.jsonl

- 代码流程：