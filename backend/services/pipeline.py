from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from pydantic import BaseModel, Field
from backend.core.config import settings
from backend.core.logger import logger
from backend.services.retrieval import retrieve_context

# Enable caching to reduce latency and API cost
set_llm_cache(InMemoryCache())

# Define expected structured output
class LLMOutput(BaseModel):
    classification: str = Field(description="REAL or FAKE")
    confidence_score: float = Field(description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(description="Bullet points explaining the reasoning")

# Configure LLM
llm = ChatGroq(
    api_key=settings.groq_api_key,
    model_name=settings.groq_model,
    temperature=0.2,
    max_tokens=1024
)

# Output parser
parser = JsonOutputParser(pydantic_object=LLMOutput)

# Prompt template
prompt_template = """
You are an advanced fake news detection assistant. Your job is to verify the authenticity of a news headline or article based on current real-world events, media coverage, and plausibility.

Use the provided Retrieved Context to cross-check factual claims. If the context does not contain relevant info, rely on your internal knowledge but state so in your reasoning.

Headline/Article: "{text}"

Retrieved Context:
{context}

{format_instructions}

Respond STRICTLY in the requested JSON format. Do not add any additional text.
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["text", "context"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# Build LangChain sequence
chain = prompt | llm | parser

def analyze_news(text: str) -> dict:
    logger.info(f"Starting analysis for text: {text[:50]}...")
    
    # 1. Retrieve context
    context_list = retrieve_context(text)
    context_str = "\n".join(context_list) if context_list else "No retrieved context available."
    logger.debug(f"Context retrieved: {context_list}")

    # 2. Run LangChain
    try:
        result = chain.invoke({"text": text, "context": context_str})
        logger.info(f"LLM Classification Result: {result.get('classification')} (Score: {result.get('confidence_score')})")
        
        # 3. Fallback logic
        confidence = float(result.get("confidence_score", 0.0))
        if confidence < settings.confidence_threshold:
            logger.warning(f"Confidence {confidence} is below threshold {settings.confidence_threshold}. Falling back to UNCERTAIN.")
            result["classification"] = "UNCERTAIN"
            result["reasoning"] = f"[FALLBACK] Model confidence ({confidence}) was below threshold. Original reasoning: {result.get('reasoning')}"
            
        return {
            "classification": result.get("classification"),
            "confidence_score": confidence,
            "reasoning": result.get("reasoning"),
            "retrieved_context": context_list
        }
    except Exception as e:
        logger.error(f"Error during LLM inference: {e}")
        return {
            "classification": "ERROR",
            "confidence_score": 0.0,
            "reasoning": f"Inference failed: {str(e)}",
            "retrieved_context": context_list
        }
