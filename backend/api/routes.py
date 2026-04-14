from fastapi import APIRouter, HTTPException
from backend.models.schemas import NewsRequest, NewsResponse
from backend.services.pipeline import analyze_news
from backend.core.logger import logger

router = APIRouter()

@router.post("/verify", response_model=NewsResponse)
async def verify_news(request: NewsRequest):
    logger.info("Received /verify request")
    text = request.text
    if len(text) > 5000:
        logger.warning("Input text too long. Truncating to 5000 characters.")
        text = text[:5000]

    result = analyze_news(text)
    
    if result["classification"] == "ERROR":
        raise HTTPException(status_code=500, detail=result["reasoning"])
        
    return NewsResponse(
        classification=result["classification"],
        confidence_score=result["confidence_score"],
        reasoning=result["reasoning"],
        retrieved_context=result["retrieved_context"]
    )
