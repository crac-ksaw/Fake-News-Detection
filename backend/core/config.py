from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str = ""
    groq_model: str = "llama3-8b-8192"
    app_name: str = "Fake News Detection API"
    confidence_threshold: float = 0.70
    faiss_index_path: str = "faiss_index"

    class Config:
        env_file = ".env"

settings = Settings()
