# 首先手动清洗和标注一下600多条服从的指令
# 主要 -- 剔除轮次相关的信息
# 把一些类似的指令合在一类
# 把矛盾的指令区分开
# 对于每条数据 从每一类抽出一个指令得到list 
# 重复x次进行数据扩充
# 然后对于completion or chosen rejected使用对应的reward打分得到优秀回答 不过似乎GRPO暂时不需要completion
from datasets import load_dataset, concatenate_datasets
import pandas as pd
import json
try:
    from kst_instruct_following.similarity_duplicator import Duplicator # 会载入一个bge embedding model

except:
    from similarity_duplicator import Duplicator


class Instruction_constructor():
    def __init__(self,instruction_file='../../dataset/约束_new.xlsx'):
        self.instruction_file = instruction_file
        self.instruction_cluster_dict = None
        self.dict_save_file = '../../dataset/instruction_cluster_dict.json'
    def load_instructions(self):
        instruction_types = ['问诊相关','套电相关','通用相关']
        instruction_cluster_dict = {_type:{} for _type in instruction_types}
        for instruction_type in instruction_types:
            df = pd.read_excel(self.instruction_file, sheet_name=instruction_type)
            columns = df.columns
            for column in columns:
                instructions = df[column].dropna().tolist()
                # cluster_instructions = Duplicator.clean_completion_by_similarity(instructions)
                cluster_instructions = self.handle_cluster_by_claude(instructions)
                instruction_cluster_dict[instruction_type][column] = cluster_instructions
                print('already clustered', instruction_type, column)
        self.instruction_cluster_dict = instruction_cluster_dict
    def handle_cluster_by_claude(self,instructions):
        cluster_instuction = []
        for ins in instructions:
            inss = ins.split('<sep>')
            cluster_instuction.append(inss)
        return cluster_instuction

    def save_instruction_cluser_dict(self):
        with open(self.dict_save_file, 'w', encoding='utf-8') as f:
            json.dump(self.instruction_cluster_dict, f, ensure_ascii=False, indent=4)
        print('already saved cluster dict')
    

if __name__ == '__main__':
    # Dup = Duplicator(eps=0.3,min_sample=3)
    Inst = Instruction_constructor()
    Inst.load_instructions()
    Inst.save_instruction_cluser_dict()
