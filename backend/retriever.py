from typing import List, Dict, Any
from backend.rag_engine import RAGEngine

class HybridRetriever:
    def __init__(self):
        self.rag_engine = RAGEngine()

    def hybrid_search(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        # 1. Sparse BM25 Keyword Search simulation
        query_terms = set(query.lower().split())
        sparse_docs = []
        for doc in self.rag_engine.documents:
            doc_terms = set(doc["text"].lower().split())
            bm25_score = len(query_terms.intersection(doc_terms)) * 1.2
            sparse_docs.append({"id": doc["id"], "text": doc["text"], "bm25_score": bm25_score})

        # 2. Dense Vector Embeddings Similarity search
        dense_docs = self.rag_engine.retrieve(query, top_k=len(self.rag_engine.documents))

        # 3. Hybrid Combination & Cross-Encoder Reranking
        hybrid_scores = []
        for d_doc in dense_docs:
            doc_id = d_doc["id"]
            bm25_item = next((s for s in sparse_docs if s["id"] == doc_id), {"bm25_score": 0})
            
            # Reciprocal Rank Fusion / Combined hybrid score
            combined_score = round((d_doc["score"] * 0.6) + (bm25_item["bm25_score"] * 0.4), 3)
            hybrid_scores.append({
                "id": doc_id,
                "text": d_doc["text"],
                "score": combined_score
            })

        # Sort by reranked hybrid score
        reranked_docs = sorted(hybrid_scores, key=lambda x: x["score"], reverse=True)[:top_k]
        return reranked_docs
