from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingsModel:
    def __init__(self, model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
        """
        初始化Embeddings模型
        
        Args:
            model_name: 模型名称，默认使用多语言的MiniLM模型
        """
        self.model = SentenceTransformer(model_name)
    
    def encode(self, text):
        """
        将文本编码为向量
        
        Args:
            text: 输入文本
            
        Returns:
            文本的向量表示
        """
        return self.model.encode(text)
    
    def similarity(self, text1, text2):
        """
        计算两个文本的相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            
        Returns:
            两个文本的余弦相似度
        """
        embedding1 = self.encode(text1)
        embedding2 = self.encode(text2)
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))