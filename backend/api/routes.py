from fastapi import APIRouter, HTTPException
from backend.models.schemas import NewsRequest, NewsResponse
from backend.services.pipeline import analyze_news
from backend.core.logger import logger

router = APIRouter()

@router.post("/verify", response_model=NewsResponse)
async def verify_news(request: NewsRequest):
    logger.info("Received /verify request")
    # For very long text, we could chunk here or in the pipeline.
    # The Pydantic model ensures text is at least 10 chars.
    if len(request.text) > 5000:
        logger.warning("Input text too long. Truncating to 5000 characters.")
        request.text = request.text[:5000]

    result = analyze_news(request.text)
    
    if result["classification"] == "ERROR":
        raise HTTPException(status_code=500, detail=result["reasoning"])
        
    return NewsResponse(
        classification=result["classification"],
        confidence_score=result["confidence_score"],
        reasoning=result["reasoning"],
        retrieved_context=result["retrieved_context"]
    )
