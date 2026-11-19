"""Shared contract for specialist agents."""

from time import perf_counter
from typing import Dict, Any


class BaseAgent:
    name = "Base Agent"

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        started = perf_counter()
        try:
            result = self.calculate(payload)
            status = "success"
            error = None
        except Exception as exc:
            result = {}
            status = "error"
            error = str(exc)
        return {
            "status": status,
            "key_results": result,
            "ai_insights": [],
            "recommendations": [],
            "errors": [error] if error else [],
            "warnings": [],
            "execution_time": round(perf_counter() - started, 4),
        }

    def calculate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
