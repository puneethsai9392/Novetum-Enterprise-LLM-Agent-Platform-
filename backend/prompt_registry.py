# Versioned Prompt Registry (v1, v2, v3)

PROMPT_REGISTRY = {
    "v1": {
        "system": "You are a basic AI assistant.",
        "cot": "Reason through this step-by-step:\nContext: {context}\nQuery: {query}"
    },
    "v2": {
        "system": "You are a Senior AI Architecture & Coding Agent adhering strictly to Chain-of-Thought (CoT) grounded execution.",
        "cot": """
<system_instructions>
Analyze the input query using explicit step-by-step reasoning.
Context:
{context}

Query: {query}
</system_instructions>
<thinking>
1. Evaluate memory context and tool outputs.
2. Formulate grounded answer without hallucination.
</thinking>
""",
        "critic": """
Evaluate answer quality (1-10):
Query: {query}
Answer: {response}
Output JSON: {{"score": 9.5, "verdict": "PASSED"}}
"""
    }
}

def get_prompt(version: str = "v2", prompt_type: str = "cot") -> str:
    return PROMPT_REGISTRY.get(version, {}).get(prompt_type, PROMPT_REGISTRY["v2"]["cot"])
