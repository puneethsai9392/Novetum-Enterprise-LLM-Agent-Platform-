import pytest
import asyncio
from backend.agent import LangGraphAgentWorkflow
from backend.eval_framework import AdvancedEvaluationFramework

def test_agent_execution():
    workflow = LangGraphAgentWorkflow()
    res = asyncio.run(workflow.run("Explain Hybrid RAG"))
    assert "response" in res
    assert res["intent"] == "HYBRID_RAG"

def test_knowledge_base_node():
    workflow = LangGraphAgentWorkflow()
    res = asyncio.run(workflow.run("What is LangGraph?"))
    assert res["intent"] == "KNOWLEDGE_BASE"
    assert "framework for building stateful" in res["response"].lower()

def test_coding_agent_mcp():
    workflow = LangGraphAgentWorkflow()
    res = asyncio.run(workflow.run("Write python code for factorial"))
    assert res["intent"] == "MCP_TOOL"

def test_eval_framework():
    framework = AdvancedEvaluationFramework()
    res = asyncio.run(framework.run_evaluations())
    assert res["accuracy_percentage"] >= 75.0
