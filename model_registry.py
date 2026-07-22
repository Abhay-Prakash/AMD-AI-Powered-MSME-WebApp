from app.ai.types import AICapability, ModelConfig
from app.core.config import settings


class ModelRegistry:
    """Maps AI capabilities to provider/model choices."""

    def __init__(self) -> None:
        self.provider = "fireworks"

    def get_model_config(self, capability: AICapability) -> ModelConfig:
        return ModelConfig(
            provider=self.provider,
            model=self.model_for(capability),
            capability=capability,
            enabled=True,
        )

    def model_for(self, capability: AICapability) -> str:
        if capability == "chat" and settings.kimi_enabled and settings.kimi_chat_model:
            return settings.kimi_chat_model

        if capability in {
            "reasoning",
            "planning",
            "chat",
            "eligibility_explanation",
            "application_drafting",
            "subsidydesk_copilot",
            "intent_detection",
        }:
            return settings.fireworks_reasoning_model

        if capability in {
            "document_understanding",
            "ocr_document_understanding",
            "document_summary",
        }:
            return settings.fireworks_document_model

        if capability == "embedding":
            return settings.fireworks_embedding_model

        if capability == "reranking":
            return settings.fireworks_reranker_model

        raise ValueError(f"Unsupported AI capability: {capability}")
