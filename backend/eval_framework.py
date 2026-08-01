import asyncio
import time
from typing import Dict, Any, List
from backend.agent import LangGraphAgentWorkflow

EVAL_BENCHMARK_SUITE = [
    {
        "query": "What is LangGraph used for in AI Agent architectures?",
        "expected_keywords": ["langgraph", "stateful", "agent"],
        "min_faithfulness_score": 0.8,
        "max_latency_ms": 3000
    },
    {
        "query": "How does Model Context Protocol (MCP) work?",
        "expected_keywords": ["mcp", "protocol", "tools"],
        "min_faithfulness_score": 0.8,
        "max_latency_ms": 3000
    },
    {
        "query": "Write python code to calculate squares of numbers",
        "expected_keywords": ["python", "repl"],
        "min_faithfulness_score": 0.9,
        "max_latency_ms": 3000
    },
    {
        "query": "Search wikipedia for distributed AI observability",
        "expected_keywords": ["wikipedia", "mcp"],
        "min_faithfulness_score": 0.85,
        "max_latency_ms": 3000
    }
]

class AdvancedEvaluationFramework:
    def __init__(self):
        self.workflow = LangGraphAgentWorkflow()

    async def run_evaluations(self) -> Dict[str, Any]:
        test_results = []
        passed_count = 0
        total_latency = 0.0
        total_faithfulness = 0.0
        total_relevancy = 0.0

        for item in EVAL_BENCHMARK_SUITE:
            t0 = time.time()
            res = await self.workflow.run(item["query"])
            duration_ms = (time.time() - t0) * 1000
            total_latency += duration_ms

            response_text = res.get("response", "").lower()
            keyword_match = any(kw in response_text for kw in item["expected_keywords"])
            
            # Metric simulations: Faithfulness, Relevancy, Context Precision
            faithfulness_score = 0.95 if keyword_match else 0.4
            relevancy_score = 0.98 if duration_ms <= item["max_latency_ms"] else 0.7
            context_precision = 0.92 if res.get("context") else 0.5

            total_faithfulness += faithfulness_score
            total_relevancy += relevancy_score

            is_passed = keyword_match and (duration_ms <= item["max_latency_ms"])
            if is_passed:
                passed_count += 1

            test_results.append({
                "query": item["query"],
                "passed": is_passed,
                "latency_ms": round(duration_ms, 2),
                "faithfulness_score": faithfulness_score,
                "relevancy_score": relevancy_score,
                "context_precision": context_precision,
                "response_snippet": res.get("response", "")[:90] + "..."
            })

        n = len(EVAL_BENCHMARK_SUITE)
        return {
            "total_benchmark_cases": n,
            "passed_cases": passed_count,
            "failed_cases": n - passed_count,
            "accuracy_percentage": round((passed_count / n) * 100, 2),
            "avg_latency_ms": round(total_latency / n, 2),
            "avg_faithfulness": round(total_faithfulness / n, 2),
            "avg_relevancy": round(total_relevancy / n, 2),
            "test_results": test_results
        }
