import re
from typing import Any

from app.ai.context_builder import ContextBuilder
from app.ai.gateway import AIGateway
from app.ai.prompt_manager import PromptManager
from app.ai.types import AIRequest, AIResponse
from app.ai.tools.registry import ToolRegistry
from app.ai.tools.executor import ToolExecutor


class AIOrchestrator:
    """Coordinates AI workflows without knowing provider SDK details."""

    def __init__(
        self,
        gateway: AIGateway | None = None,
        prompt_manager: PromptManager | None = None,
        context_builder: ContextBuilder | None = None,
    ) -> None:
        self.gateway = gateway or AIGateway()
        self.prompt_manager = prompt_manager or PromptManager()
        self.context_builder = context_builder or ContextBuilder()
        
        self.tool_registry = ToolRegistry()
        self.tool_executor = ToolExecutor(self.tool_registry)
        
        # Register a mock tool
        def update_tracker(application_id: str, status: str):
            """Updates the status of a subsidy application in the tracker."""
            return f"Successfully updated application {application_id} to status '{status}'."
        self.tool_registry.register(update_tracker)

    async def retrieve_knowledge(
        self,
        query: str,
        retrieval_service: Any,
        embedding_service: Any,
        top_k: int | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Orchestrates embedding generation and semantic retrieval without invoking LLMs."""
        import time
        start_embed = time.perf_counter()
        query_embedding = await embedding_service.embed_query(query)
        embedding_latency_ms = int((time.perf_counter() - start_embed) * 1000)
        
        embedding_model = embedding_service.gateway.model_registry.model_for("embedding")
        
        response = await retrieval_service.search(
            query=query,
            query_embedding=query_embedding,
            embedding_model=embedding_model,
            embedding_latency_ms=embedding_latency_ms,
            top_k=top_k,
            filters=filters,
        )
        # Convert RetrievalResult objects to dicts for ContextBuilder
        return [result.model_dump() for result in response.results]

    async def explain_eligibility(
        self,
        *,
        rule_result: dict[str, Any],
        business_profile: dict[str, Any] | None = None,
        knowledge_base_results: list[dict[str, Any]] | None = None,
        retrieved_documents: list[dict[str, Any]] | None = None,
    ) -> AIResponse:
        context = self.context_builder.build(
            business_profile=business_profile,
            matched_rules=rule_result.get("matched_rules", []),
            missing_rules=rule_result.get("missing_rules", []),
            knowledge_base_results=knowledge_base_results,
            retrieved_documents=retrieved_documents,
            missing_documents=rule_result.get("missing_documents", []),
            rule_result=rule_result,
        )
        request = AIRequest(
            capability="eligibility_explanation",
            system_prompt=self.prompt_manager.get_prompt("eligibility_explanation"),
            user_prompt=(
                "Explain the deterministic eligibility result using this structured context. "
                "Do not decide or modify eligibility.\n"
                f"{self.context_builder.render(context)}"
            ),
            context=context,
            temperature=0.1,
            expect_json=True,
        )
        return await self.gateway.generate_text(request)

    async def draft_application(
        self,
        *,
        business_profile: dict[str, Any],
        rule_result: dict[str, Any],
        scheme: dict[str, Any],
        missing_documents: list[str] | None = None,
    ) -> AIResponse:
        context = self.context_builder.build(
            business_profile=business_profile,
            rule_result=rule_result,
            missing_documents=missing_documents,
            extra={"scheme": scheme},
        )
        request = AIRequest(
            capability="application_drafting",
            system_prompt=self.prompt_manager.get_prompt("application_drafting"),
            user_prompt=(
                "Draft application material from this structured context. "
                "Mention missing documents separately.\n"
                f"{self.context_builder.render(context)}"
            ),
            context=context,
            temperature=0.2,
            expect_json=True,
        )
        return await self.gateway.generate_text(request)

    async def detect_intent(self, text: str) -> str:
        """Hybrid intent router."""
        text_lower = text.lower()
        if re.search(r'\b(eligibility|eligible)\b', text_lower):
            return "Eligibility"
        if re.search(r'\b(draft|application|apply)\b', text_lower):
            return "Draft Generation"
        if re.search(r'\b(tracker|status)\b', text_lower):
            return "Tracker"
        if re.search(r'\b(invoice|billing|fee|payment)\b', text_lower):
            return "Billing"
        if re.search(r'\b(client|profile)\b', text_lower):
            return "Client Specific"
        if re.search(r'\b(scheme|subsidy|pmegp|clcss)\b', text_lower):
            return "General Scheme Question"
        if re.search(r'\b(document|gst|pdf)\b', text_lower):
            return "Knowledge Search"
            
        # Fallback to LLM
        request = AIRequest(
            capability="intent_detection",
            system_prompt=self.prompt_manager.get_prompt("intent_detection"),
            user_prompt=f"Message: {text}",
            context=self.context_builder.build(),
            temperature=0.0,
        )
        response = await self.gateway.generate_text(request)
        return response.content.strip() if response.success else "General Scheme Question"

    async def chat(
        self,
        *,
        question: str,
        retrieval_service: Any,
        embedding_service: Any,
        conversation_history: list[dict[str, str]] | None = None,
        context_data: dict[str, Any] | None = None,
    ) -> tuple[AIResponse, list[dict[str, Any]], dict[str, Any]]:
        # 1. Detect Intent
        intent = await self.detect_intent(question)
        
        # 2. Retrieve Semantic Knowledge
        # Always retrieve semantic evidence before generation
        knowledge_results = await self.retrieve_knowledge(
            query=question,
            retrieval_service=retrieval_service,
            embedding_service=embedding_service,
            top_k=5,
        )
        
        # 3. Assemble Prompt Context
        ctx_kwargs = context_data or {}
        ctx_kwargs["knowledge_base_results"] = knowledge_results
        ctx_kwargs["conversation_history"] = conversation_history
        ctx_kwargs["extra"] = {"detected_intent": intent}
        
        context = self.context_builder.build(**ctx_kwargs)
        
        # 4. LLM Generation
        # Append tool instructions
        tool_instructions = self.tool_registry.get_prompt_instructions()
        if tool_instructions:
            system_prompt = self.prompt_manager.get_prompt("subsidydesk_copilot") + "\n\n" + tool_instructions
        else:
            system_prompt = self.prompt_manager.get_prompt("subsidydesk_copilot")

        request = AIRequest(
            capability="subsidydesk_copilot",
            system_prompt=system_prompt,
            user_prompt=f"Question: {question}\nContext:\n{self.context_builder.render(context)}",
            context=context,
            temperature=0.2,
        )
        
        response = await self.gateway.generate_text(request)
        
        # Handle Tool Call Loop (ReAct style)
        max_tool_loops = 3
        loops = 0
        while loops < max_tool_loops:
            if not response.success:
                break
                
            tool_call = self.tool_executor.parse_tool_call(response.content)
            if not tool_call:
                break # No tool call found, break loop
                
            # Execute tool
            observation = await self.tool_executor.execute(tool_call, context_kwargs={"session": None})
            
            # Append to prompt and call again
            request.user_prompt += f"\n\nAssistant attempted tool: {tool_call['name']}\nObservation: {observation}\nNow provide the final response to the user."
            response = await self.gateway.generate_text(request)
            loops += 1
        
        metadata = {
            "intent": intent,
            "provider": response.provider,
            "model": response.model,
            "latency_ms": response.latency_ms,
            "retrieved_chunks": len(knowledge_results),
            "generation_status": "success" if response.success else "error"
        }
        
        return response, knowledge_results, metadata

    async def summarize_document(
        self,
        *,
        document_text: str,
        business_profile: dict[str, Any] | None = None,
    ) -> AIResponse:
        context = self.context_builder.build(
            business_profile=business_profile,
            retrieved_documents=[{"content": document_text}],
        )
        request = AIRequest(
            capability="document_summary",
            system_prompt=self.prompt_manager.get_prompt("document_summary"),
            user_prompt=f"Summarize this document context:\n{self.context_builder.render(context)}",
            context=context,
            temperature=0.1,
        )
        return await self.gateway.generate_text(request)
