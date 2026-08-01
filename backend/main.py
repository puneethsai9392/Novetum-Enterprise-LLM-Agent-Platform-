import asyncio
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any
from backend.agent import LangGraphAgentWorkflow
from backend.observability import get_observability_summary
from backend.eval_framework import AdvancedEvaluationFramework
from backend.kb_routes import register_kb_endpoints

app = FastAPI(
    title="Enterprise AI Agent Platform API (Novetum Architecture)",
    description="LangGraph multi-node agent state graph, Memory, Hybrid Retrieval RAG, Python REPL MCP Coding Agent, Observability, and Evals.",
    version="2.0.0"
)

register_kb_endpoints(app)

agent_workflow = LangGraphAgentWorkflow()
eval_framework = AdvancedEvaluationFramework()

class ChatRequest(BaseModel):
    query: str
    session_id: str = "default_session"

@app.get("/")
def health_check():
    return {"status": "online", "system": "Novetum Enterprise LLM Platform v2.0"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest) -> Dict[str, Any]:
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    res = await agent_workflow.run(query=request.query, session_id=request.session_id)
    return res

@app.get("/api/chat/stream")
async def chat_stream_endpoint(query: str):
    """Server-Sent Events (SSE) Streaming endpoint."""
    async def event_generator():
        res = await agent_workflow.run(query=query)
        words = res.get("response", "").split()
        for word in words:
            yield f"data: {json.dumps({'token': word + ' '})}\n\n"
            await asyncio.sleep(0.05)
        yield "data: [DONE]\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/observability/logs")
def observability_endpoint() -> Dict[str, Any]:
    return get_observability_summary()

@app.post("/api/eval/run")
async def run_eval_endpoint() -> Dict[str, Any]:
    return await eval_framework.run_evaluations()
