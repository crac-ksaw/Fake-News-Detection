from pydantic import BaseModel, Field

class NewsRequest(BaseModel):
    text: str = Field(..., min_length=10, description="The news headline or article text to verify.")

class NewsResponse(BaseModel):
    classification: str = Field(..., description="REAL, FAKE, or UNCERTAIN")
    confidence_score: float = Field(..., description="Confidence score from 0.0 to 1.0")
    reasoning: str = Field(..., description="Detailed explanation for the classification")
    retrieved_context: list[str] = Field(default_factory=list, description="Any contextual facts retrieved")
