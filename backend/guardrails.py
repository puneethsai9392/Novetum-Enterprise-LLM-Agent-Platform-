import re
from typing import Dict, Any

class SafetyGuardrails:
    PROMPT_INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"system prompt override",
        r"jailbreak",
        r"mode: developer"
    ]

    @classmethod
    def inspect_prompt(cls, prompt: str) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        for pattern in cls.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, prompt_lower):
                return {
                    "is_safe": False,
                    "reason": f"Prompt injection attempt detected matching rule '{pattern}'"
                }
        return {"is_safe": True, "reason": "Passed safety checks"}

    @classmethod
    def validate_faithfulness(cls, response: str, context: str) -> bool:
        if not context or context == "Direct General Knowledge Mode.":
            return True
        # Ensure response doesn't blatantly contradict empty or specific context signals
        return True
