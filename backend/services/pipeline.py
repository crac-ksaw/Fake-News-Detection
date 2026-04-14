import json
from functools import lru_cache

from groq import Groq
from pydantic import BaseModel, Field

from backend.core.config import settings
from backend.core.logger import logger
from backend.services.retrieval import retrieve_context


class LLMOutput(BaseModel):
    classification: str = Field(description="REAL, FAKE, or UNCERTAIN")
    confidence_score: float = Field(description="Confidence score between 0.0 and 1.0")
    reasoning: str | list[str] = Field(
        description="Short markdown bullet points explaining the reasoning"
    )


SYSTEM_PROMPT = """
You are a fake news detection assistant.
Classify the supplied news content as REAL, FAKE, or UNCERTAIN using the retrieved live news evidence first.
Return valid JSON with exactly these keys:
- classification: one of REAL, FAKE, UNCERTAIN
- confidence_score: a float between 0 and 1
- reasoning: concise markdown bullet points
Rules:
- Prefer the retrieved evidence over prior knowledge.
- If the evidence weakly matches or there are no relevant live articles, use UNCERTAIN.
- Use REAL only when the claim is materially supported by the retrieved evidence.
- Use FAKE only when the claim is contradicted by the retrieved evidence or is clearly fabricated.
""".strip()


@lru_cache(maxsize=1)
def get_groq_client() -> Groq:
    api_key = settings.groq_api_key.strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    return Groq(
        api_key=api_key,
        timeout=settings.groq_timeout_seconds,
    )


def _normalize_result(payload: dict) -> LLMOutput:
    classification = str(payload.get("classification", "UNCERTAIN")).strip().upper()
    if classification not in {"REAL", "FAKE", "UNCERTAIN"}:
        classification = "UNCERTAIN"

    try:
        confidence_score = float(payload.get("confidence_score", 0.0))
    except (TypeError, ValueError):
        confidence_score = 0.0

    confidence_score = max(0.0, min(1.0, confidence_score))

    raw_reasoning = payload.get("reasoning", "")
    if isinstance(raw_reasoning, list):
        reasoning_items = [str(item).strip() for item in raw_reasoning if str(item).strip()]
        reasoning: str | list[str] = reasoning_items or ["No reasoning provided."]
    else:
        reasoning = str(raw_reasoning).strip() or "No reasoning provided."

    return LLMOutput(
        classification=classification,
        confidence_score=confidence_score,
        reasoning=reasoning,
    )


def _reasoning_to_markdown(reasoning: str | list[str]) -> str:
    if isinstance(reasoning, list):
        items = [item.lstrip("-* ").strip() for item in reasoning if item.strip()]
        return "\n".join(f"- {item}" for item in items) or "- No reasoning provided."

    text = reasoning.strip()
    if not text:
        return "- No reasoning provided."
    if text.startswith(("-", "*")):
        return text
    return f"- {text}"


def _request_analysis(text: str, retrieved_context: list[str]) -> LLMOutput:
    client = get_groq_client()
    evidence_block = "\n".join(f"- {item}" for item in retrieved_context) or "- No live articles found."
    completion = client.chat.completions.create(
        model=settings.groq_model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Analyze this news content and return JSON only.\n\n"
                    f"Claim:\n{text}\n\n"
                    f"Retrieved live evidence:\n{evidence_block}"
                ),
            },
        ],
    )

    message = completion.choices[0].message.content or "{}"
    return _normalize_result(json.loads(message))


def analyze_news(text: str) -> dict:
    logger.info("Starting analysis for text: %s...", text[:50])
    retrieved_context = retrieve_context(text)

    try:
        result = _request_analysis(text, retrieved_context)
        logger.info(
            "LLM Classification Result: %s (Score: %.2f)",
            result.classification,
            result.confidence_score,
        )

        confidence = result.confidence_score
        classification = result.classification
        reasoning = _reasoning_to_markdown(result.reasoning)

        if confidence < settings.confidence_threshold:
            logger.warning(
                "Confidence %.2f is below threshold %.2f. Falling back to UNCERTAIN.",
                confidence,
                settings.confidence_threshold,
            )
            classification = "UNCERTAIN"
            reasoning = (
                f"- Model confidence ({confidence:.2f}) was below threshold.\n"
                f"- Original reasoning: {reasoning.lstrip('- ').strip()}"
            )

        return {
            "classification": classification,
            "confidence_score": confidence,
            "reasoning": reasoning,
            "retrieved_context": retrieved_context,
        }
    except Exception as exc:
        logger.error("Error during LLM inference: %s", exc)
        return {
            "classification": "ERROR",
            "confidence_score": 0.0,
            "reasoning": f"Inference failed: {exc}",
            "retrieved_context": retrieved_context,
        }
