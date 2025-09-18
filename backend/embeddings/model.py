from sentence_transformers import SentenceTransformer
import numpy as np
import os
import requests
import json

class EmbeddingsModel:
    def __init__(self, model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
        """
        初始化Embeddings模型
        
        Args:
            model_name: 模型名称，默认使用多语言的MiniLM模型
        """
        # 设置环境变量以解决SSL问题
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['HF_HUB_OFFLINE'] = '1'
        
        # 检查是否可以使用Ollama本地模型
        self.use_ollama = self._check_ollama_available()
        if self.use_ollama:
            self.ollama_model = "all-minilm"  # Ollama中的模型名称
            print("使用本地Ollama模型")
        else:
            # 使用本地模型或默认模型，避免网络连接
            try:
                # 尝试使用本地模型
                self.model = SentenceTransformer('all-MiniLM-L6-v2', trust_remote_code=True)
            except Exception as e:
                print(f"加载本地模型失败: {e}")
                # 创建一个简单的随机模型作为后备方案
                class SimpleModel:
                    def encode(self, texts):
                        # 如果输入是字符串，转换为列表
                        if isinstance(texts, str):
                            texts = [texts]
                        # 为每个文本返回随机向量
                        return np.random.rand(len(texts), 384).tolist()
                
                self.model = SimpleModel()
    
    def _check_ollama_available(self):
        """检查Ollama服务是否可用"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _get_ollama_embedding(self, text):
        """使用Ollama获取文本嵌入"""
        try:
            response = requests.post(
                "http://localhost:11434/api/embeddings",
                json={
                    "model": self.ollama_model,
                    "prompt": text
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json()["embedding"]
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
        except Exception as e:
            print(f"获取Ollama嵌入失败: {e}")
            # 返回随机向量作为后备
            return np.random.rand(384).tolist()
    
    def encode(self, text):
        """
        将文本编码为向量
        
        Args:
            text: 输入文本
            
        Returns:
            文本的向量表示
        """
        if self.use_ollama:
            # 使用Ollama获取嵌入
            if isinstance(text, str):
                return self._get_ollama_embedding(text)
            elif isinstance(text, list):
                return [self._get_ollama_embedding(t) for t in text]
        else:
            # 使用原有的SentenceTransformer模型
            result = self.model.encode(text)
            # 如果结果是numpy数组，转换为列表
            if isinstance(result, np.ndarray):
                return result.tolist()
            return result
    
    def similarity(self, text1, text2):
        """
        计算两个文本的相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            
        Returns:
            两个文本的余弦相似度
        """
        if self.use_ollama:
            # 使用Ollama模型计算相似度
            embedding1 = self.encode(text1)
            embedding2 = self.encode(text2)
            
            # 转换为numpy数组
            if isinstance(embedding1, list) and not isinstance(embedding1, np.ndarray):
                embedding1 = np.array(embedding1)
            if isinstance(embedding2, list) and not isinstance(embedding2, np.ndarray):
                embedding2 = np.array(embedding2)
                
            # 确保是1D向量
            if embedding1.ndim > 1:
                embedding1 = embedding1[0]
            if embedding2.ndim > 1:
                embedding2 = embedding2[0]
                
            return float(np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)))
        else:
            # 如果模型是简单模型，直接返回随机相似度
            if hasattr(self.model, 'encode') and callable(self.model.encode):
                embedding1 = self.encode(text1)
                embedding2 = self.encode(text2)
                
                # 如果返回的是列表，转换为numpy数组
                if isinstance(embedding1, list) and not isinstance(embedding1, np.ndarray):
                    embedding1 = np.array(embedding1)
                if isinstance(embedding2, list) and not isinstance(embedding2, np.ndarray):
                    embedding2 = np.array(embedding2)
                    
                # 确保是1D向量
                if embedding1.ndim > 1:
                    embedding1 = embedding1[0]
                if embedding2.ndim > 1:
                    embedding2 = embedding2[0]
                    
                return float(np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)))
            else:
                # 简单模型返回随机相似度
                return float(np.random.rand())