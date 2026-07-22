from dataclasses import dataclass, field
from typing import Any, Literal

AICapability = Literal[
    "reasoning",
    "planning",
    "chat",
    "eligibility_explanation",
    "application_drafting",
    "document_understanding",
    "ocr_document_understanding",
    "document_summary",
    "embedding",
    "reranking",
    "subsidydesk_copilot",
    "intent_detection",
]


@dataclass(frozen=True)
class ModelConfig:
    provider: str
    model: str
    capability: AICapability
    enabled: bool = True


@dataclass
class AIContext:
    business_profile: dict[str, Any] | None = None
    matched_rules: list[dict[str, Any]] = field(default_factory=list)
    missing_rules: list[dict[str, Any]] = field(default_factory=list)
    knowledge_base_results: list[dict[str, Any]] = field(default_factory=list)
    retrieved_documents: list[dict[str, Any]] = field(default_factory=list)
    missing_documents: list[str] = field(default_factory=list)
    conversation_history: list[dict[str, str]] = field(default_factory=list)
    rule_result: dict[str, Any] | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "business_profile": self.business_profile,
            "matched_rules": self.matched_rules,
            "missing_rules": self.missing_rules,
            "knowledge_base_results": self.knowledge_base_results,
            "retrieved_documents": self.retrieved_documents,
            "missing_documents": self.missing_documents,
            "conversation_history": self.conversation_history,
            "rule_result": self.rule_result,
            "extra": self.extra,
        }


@dataclass
class AIRequest:
    capability: AICapability
    system_prompt: str
    user_prompt: str
    context: AIContext
    temperature: float = 0.2
    expect_json: bool = False


@dataclass
class AIResponse:
    capability: AICapability
    provider: str
    model: str
    content: str
    parsed: Any | None
    latency_ms: int
    estimated_tokens: int | None
    success: bool
    error: str | None = None
