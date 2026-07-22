from typing import Any

from app.ai.orchestrator import AIOrchestrator


class EligibilityExplainer:
    """Compatibility wrapper for eligibility explanation workflows."""

    def __init__(self, orchestrator: AIOrchestrator | None = None) -> None:
        self.orchestrator = orchestrator or AIOrchestrator()

    async def explain(self, rule_result: dict[str, Any]) -> str:
        response = await self.orchestrator.explain_eligibility(rule_result=rule_result)
        if not response.success:
            raise RuntimeError(response.error or "Eligibility explanation failed")
        return response.content
