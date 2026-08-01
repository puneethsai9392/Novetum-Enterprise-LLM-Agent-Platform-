import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

def register_kb_endpoints(app: FastAPI):
    KB_FILE = os.path.join(os.path.dirname(__file__), "knowledge_base.json")

    class KBEntry(BaseModel):
        question: str
        answer: str

    @app.get("/api/knowledge")
    def get_knowledge_entries():
        if not os.path.exists(KB_FILE):
            return []
        try:
            with open(KB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/knowledge")
    def add_knowledge_entry(entry: KBEntry):
        entries = []
        if os.path.exists(KB_FILE):
            with open(KB_FILE, "r", encoding="utf-8") as f:
                entries = json.load(f)
        entries.append({"question": entry.question, "answer": entry.answer})
        with open(KB_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
        return {"status": "success", "message": "Knowledge entry added successfully."}

    @app.delete("/api/knowledge")
    def delete_knowledge_entry(question: str):
        if not os.path.exists(KB_FILE):
            raise HTTPException(status_code=404, detail="Knowledge base empty.")
        with open(KB_FILE, "r", encoding="utf-8") as f:
            entries = json.load(f)
        filtered = [e for e in entries if e.get("question", "").lower() != question.lower()]
        with open(KB_FILE, "w", encoding="utf-8") as f:
            json.dump(filtered, f, indent=2)
        return {"status": "success", "message": "Knowledge entry deleted successfully."}
