import sqlite3
import time
import uuid
from typing import Dict, Any, List, Optional
from backend.config import OBSERVABILITY_DB_PATH

def init_observability_db():
    conn = sqlite3.connect(OBSERVABILITY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS traces (
            trace_id TEXT PRIMARY KEY,
            timestamp REAL,
            query TEXT,
            model_name TEXT,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER,
            latency_ms REAL,
            estimated_cost_usd REAL,
            status TEXT,
            response TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trace_id TEXT,
            step_name TEXT,
            step_input TEXT,
            step_output TEXT,
            latency_ms REAL,
            FOREIGN KEY (trace_id) REFERENCES traces (trace_id)
        )
    """)
    conn.commit()
    conn.close()

init_observability_db()

class TraceLogger:
    def __init__(self, query: str, model_name: str = "mock-gpt-4o"):
        self.trace_id = str(uuid.uuid4())
        self.query = query
        self.model_name = model_name
        self.start_time = time.time()
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.steps: List[Dict[str, Any]] = []

    def log_step(self, step_name: str, step_input: Any, step_output: Any, duration_ms: float):
        self.steps.append({
            "step_name": step_name,
            "step_input": str(step_input),
            "step_output": str(step_output),
            "latency_ms": duration_ms
        })

    def add_tokens(self, prompt_tok: int, comp_tok: int):
        self.prompt_tokens += prompt_tok
        self.completion_tokens += comp_tok

    def finalize(self, response: str, status: str = "SUCCESS") -> Dict[str, Any]:
        latency_ms = (time.time() - self.start_time) * 1000
        total_tokens = self.prompt_tokens + self.completion_tokens
        cost_usd = (self.prompt_tokens * 0.000005) + (self.completion_tokens * 0.000015)

        conn = sqlite3.connect(OBSERVABILITY_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO traces (
                trace_id, timestamp, query, model_name, prompt_tokens,
                completion_tokens, total_tokens, latency_ms, estimated_cost_usd, status, response
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.trace_id, time.time(), self.query, self.model_name,
            self.prompt_tokens, self.completion_tokens, total_tokens,
            latency_ms, cost_usd, status, response
        ))

        for step in self.steps:
            cursor.execute("""
                INSERT INTO agent_steps (trace_id, step_name, step_input, step_output, latency_ms)
                VALUES (?, ?, ?, ?, ?)
            """, (self.trace_id, step["step_name"], step["step_input"], step["step_output"], step["latency_ms"]))

        conn.commit()
        conn.close()

        return {
            "trace_id": self.trace_id,
            "latency_ms": latency_ms,
            "total_tokens": total_tokens,
            "estimated_cost_usd": cost_usd,
            "status": status,
            "steps": self.steps
        }

def get_observability_summary() -> Dict[str, Any]:
    conn = sqlite3.connect(OBSERVABILITY_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as cnt, SUM(total_tokens) as tokens, SUM(estimated_cost_usd) as cost, AVG(latency_ms) as avg_lat FROM traces")
    row = cursor.fetchone()
    
    cursor.execute("SELECT * FROM traces ORDER BY timestamp DESC LIMIT 20")
    recent_traces = [dict(r) for r in cursor.fetchall()]
    
    conn.close()

    return {
        "total_requests": row["cnt"] or 0,
        "total_tokens": row["tokens"] or 0,
        "total_cost_usd": row["cost"] or 0.0,
        "avg_latency_ms": row["avg_lat"] or 0.0,
        "recent_traces": recent_traces
    }
