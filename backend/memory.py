import sqlite3
import time
from typing import List, Dict, Any
from backend.config import MEMORY_DB_PATH

def init_memory_db():
    conn = sqlite3.connect(MEMORY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp REAL,
            role TEXT,
            content TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summary_memory (
            session_id TEXT PRIMARY KEY,
            summary TEXT,
            updated_at REAL
        )
    """)
    conn.commit()
    conn.close()

init_memory_db()

class ConversationMemory:
    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id

    def add_message(self, role: str, content: str):
        conn = sqlite3.connect(MEMORY_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversation_memory (session_id, timestamp, role, content) VALUES (?, ?, ?, ?)",
            (self.session_id, time.time(), role, content)
        )
        conn.commit()
        conn.close()

    def get_history(self, limit: int = 10) -> List[Dict[str, str]]:
        conn = sqlite3.connect(MEMORY_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM conversation_memory WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (self.session_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

    def get_summary(self) -> str:
        conn = sqlite3.connect(MEMORY_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT summary FROM summary_memory WHERE session_id = ?", (self.session_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else "No previous conversation summary available."
