from typing import Literal

from app.ai.gateway import AIGateway
from app.ai.types import AIContext, AIRequest, AICapability

ModelTask = Literal[
    "chat",
    "eligibility_explanation",
    "application_drafting",
    "ocr_document_understanding",
]


class FireworksProvider:
    """Backward-compatible adapter over the AI Gateway."""

    def __init__(self, gateway: AIGateway | None = None) -> None:
        self.gateway = gateway or AIGateway()

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        task: ModelTask,
        temperature: float = 0.2,
    ) -> str:
        request = AIRequest(
            capability=self._capability_for_task(task),
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=AIContext(),
            temperature=temperature,
        )
        response = await self.gateway.generate_text(request)
        if not response.success:
            raise RuntimeError(response.error or "AI provider request failed")
        return response.content

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return await self.gateway.embed_texts(texts)

    def reranker_model(self) -> str:
        return self.gateway.selected_model("reranking")

    def model_for_task(self, task: ModelTask) -> str:
        return self.gateway.selected_model(self._capability_for_task(task))

    def _capability_for_task(self, task: ModelTask) -> AICapability:
        return task
