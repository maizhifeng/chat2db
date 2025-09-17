import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量以解决SSL连接问题
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

from embeddings.model import EmbeddingsModel

def test_embeddings():
    print("Testing embeddings model...")
    try:
        # 初始化 Embeddings 模型
        embeddings_model = EmbeddingsModel()
        
        # 测试编码功能
        text = "Hello, world!"
        embedding = embeddings_model.encode(text)
        print(f"Encoding successful. Embedding shape: {embedding.shape}")
        
        # 测试相似度计算功能
        text1 = "Hello, world!"
        text2 = "Hi, there!"
        similarity = embeddings_model.similarity(text1, text2)
        print(f"Similarity calculation successful. Similarity: {similarity}")
        
        print("All tests passed!")
        return True
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_embeddings()