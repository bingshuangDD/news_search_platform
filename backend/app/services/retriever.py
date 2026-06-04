"""
TF-IDF 检索器 —— RAG 核心组件

使用 jieba 分词 + TF-IDF 向量化 + 余弦相似度检索。
所有数据存储在进程内存中，250 chunk 约 100KB，启动时从 MySQL 全量加载一次。
"""

import re
import math
from typing import Dict, List, Tuple

import jieba


# ---------- 文本分块 ----------

def split_text(text: str, chunk_size: int = 400, overlap: int = 60) -> List[str]:
    """
    按句子边界切分文本为 chunk。

    策略：
    1. 以 。！？\\n 为句子分隔符切分
    2. 逐句拼接，超过 chunk_size 时新起一个 chunk
    3. 相邻 chunk 之间保留 overlap 字的重叠，防止关键信息落在边界被切断
    """
    if not text:
        return []

    # 按句子边界切分（保留分隔符）
    sentences = re.split(r'(?<=[。！？\n])', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return []

    chunks = []
    current = ""

    for sent in sentences:
        if len(current) + len(sent) <= chunk_size:
            current += sent
        else:
            if current:
                chunks.append(current)
            # 新 chunk 从前一个 chunk 末尾取 overlap 字作为前缀
            if overlap > 0 and current:
                overlap_text = current[-overlap:] if len(current) > overlap else current
                current = overlap_text + sent
            else:
                current = sent

    if current:
        chunks.append(current)

    return chunks


# ---------- TF-IDF 检索器 ----------

class NewsRetriever:
    """基于 jieba + TF-IDF + 余弦相似度的新闻检索器"""

    def __init__(self):
        self.chunks: List[dict] = []
        self.idf: Dict[str, float] = {}
        self.tfidf_matrix: List[Dict[str, float]] = []
        self._built: bool = False

    # ---------- 分词 ----------

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """
        jieba 分词 → 过滤标点/空白/单字 → 返回词语列表。
        保留中文字符、英文字母、数字组成的词。
        """
        words = jieba.lcut(text)
        return [
            w for w in words
            if len(w) > 1 and re.search(r'[一-鿿\w]', w)
        ]

    # ---------- 添加 chunk ----------

    def add_chunk(
        self,
        news_id: int,
        title: str,
        text: str,
        category: str,
        publish_time: str,
    ) -> None:
        """追加一个新闻 chunk"""
        self.chunks.append({
            "news_id": news_id,
            "title": title,
            "text": text,
            "category": category,
            "publish_time": publish_time,
        })

    # ---------- 构建索引 ----------

    def build_index(self) -> None:
        """
        全量构建 TF-IDF 索引：
        1. 对所有 chunk 正文做分词
        2. 计算 IDF（逆文档频率）：idf = log((N+1)/(df+1)) + 1（sklearn 平滑）
        3. 为每个 chunk 构建 TF-IDF 稀疏向量
        """
        if not self.chunks:
            self._built = True
            return

        # 1) 对每个 chunk 分词
        tokenized_chunks = [self._tokenize(chunk["text"]) for chunk in self.chunks]

        # 2) 计算 DF（文档频率）
        df: Dict[str, int] = {}
        for tokens in tokenized_chunks:
            for term in set(tokens):  # 每个词在每个文档中只计一次
                df[term] = df.get(term, 0) + 1

        # 3) 计算 IDF
        N = len(self.chunks)
        self.idf = {
            term: math.log((N + 1) / (freq + 1)) + 1
            for term, freq in df.items()
        }

        # 4) 构建 TF-IDF 矩阵（稀疏向量，dict 形式）
        self.tfidf_matrix = []
        for tokens in tokenized_chunks:
            tfidf_vec: Dict[str, float] = {}
            # 计算词频
            tf: Dict[str, int] = {}
            for term in tokens:
                tf[term] = tf.get(term, 0) + 1
            # TF * IDF
            for term, freq in tf.items():
                if term in self.idf:
                    tfidf_vec[term] = freq * self.idf[term]
            self.tfidf_matrix.append(tfidf_vec)

        self._built = True

    # ---------- 余弦相似度 ----------

    @staticmethod
    def _cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """
        两个稀疏向量（dict 形式）的余弦相似度：dot / (norm1 * norm2)
        """
        # 点积：只遍历较短的向量
        if len(vec1) > len(vec2):
            vec1, vec2 = vec2, vec1

        dot = sum(vec1[k] * vec2.get(k, 0) for k in vec1)

        # L2 范数
        norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot / (norm1 * norm2)

    # ---------- 检索 ----------

    def search(self, query: str, top_k: int = 3) -> List[Tuple[dict, float]]:
        """
        检索与 query 最相似的 top_k 个 chunk。

        Returns:
            [(chunk_dict, score), ...] 按分数降序排列
        """
        if not self._built or not self.tfidf_matrix:
            return []

        # 1) 查询分词
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        # 2) 查询 TF 向量
        query_tf: Dict[str, int] = {}
        for term in query_tokens:
            query_tf[term] = query_tf.get(term, 0) + 1

        # 3) 查询 TF-IDF 向量
        query_tfidf: Dict[str, float] = {}
        for term, freq in query_tf.items():
            if term in self.idf:
                query_tfidf[term] = freq * self.idf[term]

        if not query_tfidf:
            return []

        # 4) 计算与所有 chunk 的余弦相似度
        scores = [
            (self.chunks[i], self._cosine_similarity(query_tfidf, vec))
            for i, vec in enumerate(self.tfidf_matrix)
        ]

        # 5) 排序返回
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    # ---------- 清空 ----------

    def clear(self) -> None:
        """清空所有索引数据"""
        self.chunks.clear()
        self.idf.clear()
        self.tfidf_matrix.clear()
        self._built = False


# ---------- 全局单例 ----------

retriever = NewsRetriever()
