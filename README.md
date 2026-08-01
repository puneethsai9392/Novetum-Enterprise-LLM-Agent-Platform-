# Novetum Enterprise AI Agent Platform

Production-grade LLM Application architecture designed to hit **100% coverage** for Novetum's job description.

## Architecture

```
                 User
                  │
             Streamlit UI
                  │
            FastAPI Server (REST + SSE Streaming)
                  │
       LangGraph Multi-Node Agent State Graph
   ┌──────────┬───────────┬───────────┬───────────┐
Memory     Planner    MCP Tools     Hybrid RAG   Critic
(SQLite)  (Intent)   (Python REPL   (BM25 + Dense (Groundedness
                      Wikipedia,    + CrossEncoder Evaluation)
                      Filesystem)     Reranking)
                  │
          LLMOps Observability & Automated Evals
       (Traces, Tokens, Cost, Relevancy, Faithfulness)
```

## Features Implemented

1. **LangGraph State Graph Workflows**: Stateful node traversal (`Planner` -> `Memory` -> `Tool/RAG` -> `Reasoning` -> `Critic`).
2. **Conversation Memory**: SQLite-backed session history and sliding-window summaries (`backend/memory.py`).
3. **Coding Agent via MCP Protocol**: Python REPL tool server, Wikipedia search, and filesystem access over stdio transport (`backend/mcp_server.py`).
4. **Hybrid Retrieval RAG**: BM25 Sparse Keyword Search + Dense Vector Search + Reranker (`backend/retriever.py`).
5. **Multi-Provider LLM Abstraction**: Configurable engine support for `OpenAI`, `Groq`, `Gemini`, `Ollama`, and `Mock` fallback (`backend/models.py`).
6. **Guardrails & Safety**: Prompt injection protection & faithfulness verification (`backend/guardrails.py`).
7. **Versioned Prompts**: Documented prompt registry (`v1`, `v2`, `v3`) with Chain-of-Thought (CoT) (`backend/prompt_registry.py`).
8. **Enterprise Evals Framework**: Measures **Answer Relevancy**, **Faithfulness**, **Context Precision**, **Accuracy**, and **Latency** (`backend/eval_framework.py`).
9. **LLMOps Observability**: Complete trace logger recording prompt tokens, completion tokens, latency, cost ($), tool output, and step execution details (`backend/observability.py`).
10. **SSE Response Streaming**: Server-Sent Events endpoint (`/api/chat/stream`).

## How to Run Locally

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start FastAPI Backend
```bash
uvicorn backend.main:app --reload --port 8000
```

### 3. Start Streamlit Frontend UI
```bash
streamlit run frontend/app.py
```
