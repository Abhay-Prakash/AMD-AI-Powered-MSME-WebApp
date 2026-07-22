import json
from abc import ABC, abstractmethod
from typing import Any, List

from app.ai.types import AIContext


class ContextProvider(ABC):
    @abstractmethod
    def provide(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Extract and provide specific context from kwargs."""
        pass


class ClientProvider(ContextProvider):
    def provide(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        if "business_profile" in kwargs and kwargs["business_profile"]:
            return {"business_profile": kwargs["business_profile"]}
        return {}


class KnowledgeProvider(ContextProvider):
    def provide(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        result = {}
        if "knowledge_base_results" in kwargs and kwargs["knowledge_base_results"]:
            result["knowledge_base_results"] = kwargs["knowledge_base_results"]
        if "retrieved_documents" in kwargs and kwargs["retrieved_documents"]:
            result["retrieved_documents"] = kwargs["retrieved_documents"]
        return result


class MatchProvider(ContextProvider):
    def provide(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        result = {}
        if "matched_rules" in kwargs:
            result["matched_rules"] = kwargs["matched_rules"]
        if "missing_rules" in kwargs:
            result["missing_rules"] = kwargs["missing_rules"]
        if "rule_result" in kwargs and kwargs["rule_result"]:
            result["rule_result"] = kwargs["rule_result"]
        return result


class ApplicationProvider(ContextProvider):
    def provide(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        if "missing_documents" in kwargs:
            return {"missing_documents": kwargs["missing_documents"]}
        return {}


class TrackerProvider(ContextProvider):
    def provide(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        if "tracker_status" in kwargs:
            return {"tracker_status": kwargs["tracker_status"]}
        return {}


class BillingProvider(ContextProvider):
    def provide(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        if "billing_records" in kwargs:
            return {"billing_records": kwargs["billing_records"]}
        return {}


class ContextBuilder:
    """Builds the structured context object sent to AI workflows using modular providers."""

    def __init__(self):
        self.providers: List[ContextProvider] = [
            ClientProvider(),
            KnowledgeProvider(),
            MatchProvider(),
            ApplicationProvider(),
            TrackerProvider(),
            BillingProvider(),
        ]

    def build(self, **kwargs: Any) -> AIContext:
        context_data = {}
        for provider in self.providers:
            # We can optionally filter providers by intent here if an intent is passed,
            # but providing only what is passed in kwargs is functionally equivalent
            # and keeps the builder flexible.
            provided = provider.provide(kwargs)
            context_data.update(provided)
        
        # Capture conversation history and extra directly
        context_data["conversation_history"] = kwargs.get("conversation_history") or []
        context_data["extra"] = kwargs.get("extra") or {}
        
        # Ensure we map everything cleanly into AIContext
        return AIContext(
            business_profile=context_data.get("business_profile"),
            matched_rules=context_data.get("matched_rules") or [],
            missing_rules=context_data.get("missing_rules") or [],
            knowledge_base_results=context_data.get("knowledge_base_results") or [],
            retrieved_documents=context_data.get("retrieved_documents") or [],
            missing_documents=context_data.get("missing_documents") or [],
            conversation_history=context_data.get("conversation_history") or [],
            rule_result=context_data.get("rule_result"),
            extra=context_data.get("extra") or {},
        )

    def render(self, context: AIContext) -> str:
        return json.dumps(context.to_dict(), default=str, indent=2)
