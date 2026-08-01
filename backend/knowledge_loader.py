import os
import json
from typing import Dict, Any, Optional

class KnowledgeLoader:
    def __init__(self, json_path: Optional[str] = None):
        if json_path is None:
            json_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
        self.json_path = json_path
        self.knowledge_items = self._load_json()

    def _load_json(self):
        if not os.path.exists(self.json_path):
            return []
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return []

    def search_knowledge(self, query: str, threshold: float = 0.5) -> Dict[str, Any]:
        query_words = set(query.lower().replace("?", "").replace(".", "").split())
        best_match = None
        highest_score = 0.0

        for item in self.knowledge_items:
            q_words = set(item.get("question", "").lower().replace("?", "").replace(".", "").split())
            if not q_words:
                continue
            intersection = query_words.intersection(q_words)
            score = len(intersection) / len(q_words)
            if score > highest_score:
                highest_score = score
                best_match = item

        if best_match and highest_score >= threshold:
            return {
                "match_found": True,
                "confidence_score": round(highest_score, 2),
                "answer": best_match.get("answer", ""),
                "question": best_match.get("question", ""),
                "source": "JSON Knowledge Base"
            }

        return {
            "match_found": False,
            "confidence_score": round(highest_score, 2),
            "answer": None,
            "source": "JSON Knowledge Base"
        }
