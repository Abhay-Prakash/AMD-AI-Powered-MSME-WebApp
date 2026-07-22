import logging
from datetime import UTC, datetime
from time import perf_counter
from typing import Any

from openai import AsyncOpenAI

from app.ai.model_registry import ModelRegistry
from app.ai.response_parser import ResponseParser
from app.ai.types import AICapability, AIRequest, AIResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIGateway:
    """Provider boundary for AI calls, model selection, retries, and logging."""

    def __init__(
        self,
        model_registry: ModelRegistry | None = None,
        response_parser: ResponseParser | None = None,
    ) -> None:
        self.model_registry = model_registry or ModelRegistry()
        self.response_parser = response_parser or ResponseParser()
        self._fireworks_client: AsyncOpenAI | None = None

    def _client(self, provider: str) -> AsyncOpenAI:
        if provider != "fireworks":
            raise RuntimeError("Configured AI provider is not supported")

        if not settings.fireworks_api_key:
            raise RuntimeError("FIREWORKS_API_KEY is not configured")

        if self._fireworks_client is None:
            self._fireworks_client = AsyncOpenAI(
                api_key=settings.fireworks_api_key,
                base_url=settings.fireworks_base_url,
            )
        return self._fireworks_client

    async def generate_text(self, request: AIRequest) -> AIResponse:
        config = self.model_registry.get_model_config(request.capability)
        started = perf_counter()
        estimated_tokens: int | None = None

        for attempt in range(1, settings.ai_gateway_max_retries + 1):
            try:
                client = self._client(config.provider)
                response = await client.chat.completions.create(
                    model=config.model,
                    messages=[
                        {"role": "system", "content": request.system_prompt},
                        {"role": "user", "content": request.user_prompt},
                    ],
                    temperature=request.temperature,
                )
                content = response.choices[0].message.content or ""
                usage = getattr(response, "usage", None)
                if usage is not None:
                    estimated_tokens = getattr(usage, "total_tokens", None)

                normalized, parsed = self.response_parser.parse(
                    content,
                    expect_json=request.expect_json,
                )
                latency_ms = int((perf_counter() - started) * 1000)
                self._log_call(
                    capability=request.capability,
                    model=config.model,
                    provider=config.provider,
                    latency_ms=latency_ms,
                    estimated_tokens=estimated_tokens,
                    success=True,
                    attempt=attempt,
                )
                return AIResponse(
                    capability=request.capability,
                    provider=config.provider,
                    model=config.model,
                    content=normalized,
                    parsed=parsed,
                    latency_ms=latency_ms,
                    estimated_tokens=estimated_tokens,
                    success=True,
                )
            except Exception as exc:  # noqa: BLE001
                print(f"DEBUG: Exception in generate_text: {exc}")
                latency_ms = int((perf_counter() - started) * 1000)
                self._log_call(
                    capability=request.capability,
                    model=config.model,
                    provider=config.provider,
                    latency_ms=latency_ms,
                    estimated_tokens=estimated_tokens,
                    success=False,
                    attempt=attempt,
                    error_type=exc.__class__.__name__,
                )
                if attempt >= settings.ai_gateway_max_retries:
                    return AIResponse(
                        capability=request.capability,
                        provider=config.provider,
                        model=config.model,
                        content="",
                        parsed=None,
                        latency_ms=latency_ms,
                        estimated_tokens=estimated_tokens,
                        success=False,
                        error="AI provider request failed",
                    )

        raise RuntimeError("AI gateway retry loop exited unexpectedly")

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        config = self.model_registry.get_model_config("embedding")
        started = perf_counter()
        try:
            client = self._client(config.provider)
            response = await client.embeddings.create(model=config.model, input=texts)
            latency_ms = int((perf_counter() - started) * 1000)
            usage = getattr(response, "usage", None)
            estimated_tokens = getattr(usage, "total_tokens", None) if usage is not None else None
            self._log_call(
                capability="embedding",
                model=config.model,
                provider=config.provider,
                latency_ms=latency_ms,
                estimated_tokens=estimated_tokens,
                success=True,
                attempt=1,
            )
            return [item.embedding for item in response.data]
        except Exception as exc:  # noqa: BLE001
            latency_ms = int((perf_counter() - started) * 1000)
            self._log_call(
                capability="embedding",
                model=config.model,
                provider=config.provider,
                latency_ms=latency_ms,
                estimated_tokens=None,
                success=False,
                attempt=1,
                error_type=exc.__class__.__name__,
            )
            raise RuntimeError("AI embedding request failed") from exc

    def selected_model(self, capability: AICapability) -> str:
        return self.model_registry.model_for(capability)

    def _log_call(
        self,
        *,
        capability: AICapability,
        model: str,
        provider: str,
        latency_ms: int,
        estimated_tokens: int | None,
        success: bool,
        attempt: int,
        error_type: str | None = None,
    ) -> None:
        log_payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "capability": capability,
            "provider": provider,
            "model": model,
            "latency_ms": latency_ms,
            "estimated_tokens": estimated_tokens,
            "success": success,
            "attempt": attempt,
            "error_type": error_type,
        }
        logger.info("ai_call", extra={"ai_call": log_payload})
