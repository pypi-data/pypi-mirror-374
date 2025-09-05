import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0' # 设置GPU设备
import numpy as np
import random
from FlagEmbedding import BGEM3FlagModel
from sklearn.cluster import DBSCAN
from collections import Counter

class Duplicator(): # from 振杰
    def __init__(self,eps=0.3,min_sample=2):
        self.eps = eps
        self.min_sample = min_sample
        self.model_path = '/data/public/bge-m3'
        self.model = BGEM3FlagModel(self.model_path)
    def clean_completion_by_similarity(self,completions):
        embeddings_data = self.model.encode(completions, batch_size=256, max_length=512)['dense_vecs']
        embeddings_data = embeddings_data.astype(np.float32)
        print("clutering...")
        whole_cluster_data = self.use_cuml_DBSCAN(embeddings_data)
        end_data = self.get_all_cluster_res(whole_cluster_data, completions)
        return end_data   
    
    def use_cuml_DBSCAN(self, emb_data):
        """
        使用 DBSCAN 算法对嵌入向量进行聚类

        Args:
            emb_data (list): 嵌入向量数据

        Returns:
            cluster_result: 聚类结果数组，-1 表示噪声点
        """
        clf = DBSCAN(metric="cosine", eps=self.eps, min_samples=self.min_sample)
        cluster_result = clf.fit_predict(emb_data)
        return cluster_result
    
    def get_sample_cluster_res(self, whole_cluster_data, preprocess_data):
        """
        根据聚类结果生成最终数据

        Args:
            whole_cluster_data: 聚类结果
            preprocess_data: 原始数据

        Returns:
            no_repeat_data: 去重后的数据
        """
        whole_cluster_data_count = Counter(whole_cluster_data)
        no_repeat_data = []
        for cluster_id, nums in whole_cluster_data_count.items():
            if cluster_id != -1 and nums > 1:
                object_idx = [idx for idx, j in enumerate(whole_cluster_data) if j == cluster_id]
                object_sentence = [preprocess_data[i] for i in object_idx]
                no_repeat_data.append(random.choices(object_sentence, k=1)[0])
            else:
                object_idx = [idx for idx, j in enumerate(whole_cluster_data) if j == cluster_id]
                object_sentence = [preprocess_data[i] for i in object_idx]
                for sentence in object_sentence:
                    no_repeat_data.append(sentence)
        return no_repeat_data
    
    def get_all_cluster_res(self, whole_cluster_data, preprocess_data):
        """
        根据聚类结果生成最终数据

        Args:
            whole_cluster_data: 聚类结果
            preprocess_data: 原始数据

        Returns:
            no_repeat_data: 去重后的数据
        """
        whole_cluster_data_count = Counter(whole_cluster_data)
        cluster_data = []
        for cluster_id, nums in whole_cluster_data_count.items():
            if cluster_id != -1 and nums > 1:
                object_idx = [idx for idx, j in enumerate(whole_cluster_data) if j == cluster_id]
                object_sentence = [preprocess_data[i] for i in object_idx]
                cluster_data.append(object_sentence)
            else:
                object_idx = [idx for idx, j in enumerate(whole_cluster_data) if j == cluster_id]
                object_sentence = [preprocess_data[i] for i in object_idx]
                for sentence in object_sentence:
                        cluster_data.append([sentence])
        return cluster_data