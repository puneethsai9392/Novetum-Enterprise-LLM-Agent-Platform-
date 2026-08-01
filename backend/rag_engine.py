import os
from typing import List, Dict, Any
from backend.config import CHROMA_PERSIST_DIR, EMBEDDING_MODEL_NAME

class RAGEngine:
    def __init__(self):
        self.documents = [
            {"id": "doc_1", "text": "LangGraph is a framework for building stateful, multi-actor applications with LLMs, used for core agent orchestration."},
            {"id": "doc_2", "text": "MCP (Model Context Protocol) provides an open standard for connecting AI models to tools, resources, and workflows safely via stdio or SSE transport."},
            {"id": "doc_3", "text": "Observability in LLM pipelines involves tracking latency (ms), token usage (prompt vs completion), cost ($), and execution traces per agent step."},
            {"id": "doc_4", "text": "RAG (Retrieval-Augmented Generation) combines dense embedding vector store similarity search with sparse reranking for context grounding."}
        ]

    def chunk_text(self, text: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        return chunks

    def retrieve(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        # Keyword-weighted semantic retrieval simulation with rank scoring
        query_words = set(query.lower().split())
        scored_docs = []
        for doc in self.documents:
            doc_words = set(doc["text"].lower().split())
            overlap = len(query_words.intersection(doc_words))
            score = round(0.5 + (overlap * 0.15), 3)
            scored_docs.append({"id": doc["id"], "text": doc["text"], "score": score})
        
        # Sort docs by score (Reranking phase)
        reranked_docs = sorted(scored_docs, key=lambda x: x["score"], reverse=True)[:top_k]
        return reranked_docs
