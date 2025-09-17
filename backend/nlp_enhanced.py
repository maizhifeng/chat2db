import re
from typing import Dict, List, Tuple
import numpy as np
# 导入embeddings模块
from embeddings.model import EmbeddingsModel
from embeddings.similarity import cosine_similarity

class EnhancedNLP:
    """
    增强的自然语言处理模块，用于将自然语言转换为SQL查询
    """
    
    def __init__(self, embeddings_model=None):
        # 初始化 Embeddings 模型
        self.embeddings_model = embeddings_model or EmbeddingsModel()
        
        # 定义关键词映射
        self.select_keywords = ['show', 'list', 'get', 'find', 'retrieve', 'display', 'select']
        self.count_keywords = ['count', 'how many', 'number of', 'total']
        self.insert_keywords = ['add', 'create', 'insert', 'new']
        self.update_keywords = ['update', 'modify', 'change', 'edit']
        self.delete_keywords = ['delete', 'remove', 'drop']
        
        # 预先计算各类意图的向量表示
        self.count_intent_embeddings = self._precompute_intent_embeddings(self.count_keywords)
        self.select_intent_embeddings = self._precompute_intent_embeddings(self.select_keywords)
        self.insert_intent_embeddings = self._precompute_intent_embeddings(self.insert_keywords)
        self.update_intent_embeddings = self._precompute_intent_embeddings(self.update_keywords)
        self.delete_intent_embeddings = self._precompute_intent_embeddings(self.delete_keywords)
        
        # 相似度阈值
        self.intent_threshold = 0.7
        
        # 定义操作符映射
        self.operators = {
            'greater than': '>',
            'less than': '<',
            'equal to': '=',
            'equals': '=',
            'more than': '>',
            'higher than': '>',
            'lower than': '<',
            'not equal to': '!=',
            'between': 'BETWEEN'
        }
        
        # 定义逻辑操作符
        self.logical_operators = {
            'and': 'AND',
            'or': 'OR'
        }
    
    def parse_nl_to_sql(self, nl_text: str, table_name: str = None) -> str:
        """
        将自然语言转换为SQL查询
        
        Args:
            nl_text: 自然语言文本
            table_name: 表名（可选）
            
        Returns:
            SQL查询语句
        """
        text = nl_text.strip().lower()
        
        # 使用 Embeddings 模型计算查询的语义向量
        query_embedding = self.embeddings_model.encode(nl_text)
        
        # 计算与各类操作关键词的相似度
        count_similarity = self._calculate_similarity(query_embedding, self.count_intent_embeddings)
        select_similarity = self._calculate_similarity(query_embedding, self.select_intent_embeddings)
        insert_similarity = self._calculate_similarity(query_embedding, self.insert_intent_embeddings)
        update_similarity = self._calculate_similarity(query_embedding, self.update_intent_embeddings)
        delete_similarity = self._calculate_similarity(query_embedding, self.delete_intent_embeddings)
        
        # 根据相似度确定意图
        intent_similarities = [
            (count_similarity, 'count'),
            (select_similarity, 'select'),
            (insert_similarity, 'insert'),
            (update_similarity, 'update'),
            (delete_similarity, 'delete')
        ]
        
        # 按相似度排序
        intent_similarities.sort(key=lambda x: x[0], reverse=True)
        best_similarity, best_intent = intent_similarities[0]
        
        # 根据相似度确定意图
        if best_similarity > self.intent_threshold:
            if best_intent == 'count':
                return self._parse_count_query(text, table_name)
            elif best_intent == 'select':
                return self._parse_select_query(text, table_name)
            elif best_intent == 'insert':
                return self._parse_insert_query(text, table_name)
            elif best_intent == 'update':
                return self._parse_update_query(text, table_name)
            elif best_intent == 'delete':
                return self._parse_delete_query(text, table_name)
        else:
            # 默认返回简单的SELECT查询
            return self._parse_select_query(text, table_name)
    
    def _precompute_intent_embeddings(self, keywords):
        """预先计算意图关键词的向量表示"""
        embeddings = []
        for keyword in keywords:
            embedding = self.embeddings_model.encode(keyword)
            embeddings.append(embedding)
        return embeddings
    
    def _calculate_similarity(self, query_embedding, intent_embeddings):
        """计算查询与意图向量的相似度"""
        max_similarity = 0
        for intent_embedding in intent_embeddings:
            similarity = cosine_similarity(query_embedding, intent_embedding)
            if similarity > max_similarity:
                max_similarity = similarity
        return max_similarity
    
    def _parse_count_query(self, text: str, table_name: str = None) -> str:
        """解析COUNT查询"""
        # 提取表名
        table = table_name or self._extract_table_name(text) or 'employees'
        
        # 检查是否有WHERE条件
        where_clause = self._extract_where_clause(text)
        
        if where_clause:
            return f"SELECT COUNT(*) as count FROM {table} WHERE {where_clause}"
        else:
            return f"SELECT COUNT(*) as count FROM {table}"
    
    def _parse_select_query(self, text: str, table_name: str = None) -> str:
        """解析SELECT查询"""
        # 提取表名
        table = table_name or self._extract_table_name(text) or 'employees'
        
        # 提取列名（如果有的话）
        columns = self._extract_columns(text)
        
        # 检查是否有WHERE条件
        where_clause = self._extract_where_clause(text)
        
        # 构建SELECT子句
        if columns:
            select_clause = ', '.join(columns)
        else:
            select_clause = '*'
        
        # 构建基础查询
        query = f"SELECT {select_clause} FROM {table}"
        
        # 添加WHERE子句（如果有的话）
        if where_clause:
            query += f" WHERE {where_clause}"
        
        # 添加LIMIT
        query += " LIMIT 100"
        
        return query
    
    def _parse_insert_query(self, text: str, table_name: str = None) -> str:
        """解析INSERT查询"""
        # 这是一个简化的实现，实际应用中需要更复杂的逻辑
        table = table_name or self._extract_table_name(text) or 'employees'
        return f"INSERT INTO {table} VALUES (...)"
    
    def _parse_update_query(self, text: str, table_name: str = None) -> str:
        """解析UPDATE查询"""
        # 这是一个简化的实现，实际应用中需要更复杂的逻辑
        table = table_name or self._extract_table_name(text) or 'employees'
        return f"UPDATE {table} SET ... WHERE ..."
    
    def _parse_delete_query(self, text: str, table_name: str = None) -> str:
        """解析DELETE查询"""
        # 这是一个简化的实现，实际应用中需要更复杂的逻辑
        table = table_name or self._extract_table_name(text) or 'employees'
        where_clause = self._extract_where_clause(text)
        
        if where_clause:
            return f"DELETE FROM {table} WHERE {where_clause}"
        else:
            # 为了安全起见，不支持无条件删除
            return "DELETE FROM {table} WHERE 1=0 -- Safety: Please specify conditions"
    
    def _extract_table_name(self, text: str) -> str:
        """从文本中提取表名"""
        # 查找常见的表名模式
        patterns = [
            r"from\s+(\w+)",
            r"in\s+(\w+)",
            r"table\s+(\w+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_columns(self, text: str) -> List[str]:
        """从文本中提取列名"""
        # 这是一个简化的实现
        # 在实际应用中，可能需要更复杂的自然语言理解
        
        # 查找"show [columns]"模式
        match = re.search(r"show\s+(.+?)\s+(?:from|in)", text)
        if match:
            columns_text = match.group(1)
            # 简单地按逗号分割
            columns = [col.strip() for col in columns_text.split(',')]
            return columns
        
        return []
    
    def _extract_where_clause(self, text: str) -> str:
        """从文本中提取WHERE子句"""
        # 查找WHERE条件
        where_patterns = [
            r"where\s+(.+)",
            r"with\s+(.+)",
            r"having\s+(.+)"
        ]
        
        for pattern in where_patterns:
            match = re.search(pattern, text)
            if match:
                condition_text = match.group(1)
                return self._parse_condition(condition_text)
        
        # 查找比较条件（如"where salary > 50000"）
        comparison_patterns = [
            r"(\w+)\s+(greater than|less than|equal to|equals|more than|higher than|lower than|not equal to)\s+(\w+|\d+)",
            r"(\w+)\s+between\s+(\d+)\s+and\s+(\d+)"
        ]
        
        conditions = []
        for pattern in comparison_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                if "between" in match.group(0):
                    conditions.append(f"{match.group(1)} BETWEEN {match.group(2)} AND {match.group(3)}")
                else:
                    op_text = match.group(2)
                    op = self.operators.get(op_text, '=')
                    conditions.append(f"{match.group(1)} {op} {match.group(3)}")
        
        if conditions:
            return " AND ".join(conditions)
        
        return ""
    
    def _parse_condition(self, condition_text: str) -> str:
        """解析条件文本"""
        # 这是一个简化的实现
        # 在实际应用中，可能需要更复杂的自然语言理解
        
        # 替换逻辑操作符
        for nl_op, sql_op in self.logical_operators.items():
            condition_text = condition_text.replace(nl_op, sql_op)
        
        # 替换操作符
        for nl_op, sql_op in self.operators.items():
            condition_text = condition_text.replace(nl_op, sql_op)
        
        return condition_text

# 创建全局实例
enhanced_nlp = EnhancedNLP()