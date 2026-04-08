# 🧠 Fake News Detection - Production-Grade AI Pipeline

A modular, scalable, and RAG-powered news verification system. This project refactors a monolithic script into a clean, decoupled microservices architecture designed for reliability and production-readiness.

## 🚀 Features

- **Decoupled Architecture:** Separated Frontend (Streamlit) and Backend (FastAPI).
- **RAG-Powered (Retrieval-Augmented Generation):** Contextual retrieval via FAISS and HuggingFace embeddings (`all-MiniLM-L6-v2`) to ground predictions in verified facts.
- **Advanced LLM Inference:** Integrated with **Groq (Llama-3)** for high-speed, cost-effective news analysis.
- **Robust Validation:** Pydantic models ensure inputs are clean and within length limits.
- **Confidence Thresholding:** Automatic fallback to `UNCERTAIN` classification if the model's confidence is below 70%.
- **High Performance:** Response caching via `InMemoryCache` to reduce API costs and latency.
- **Production Observability:** Structured logging with `Loguru` (local and rotating files).
- **Docker Ready:** Containerized for easy deployment on GCP, AWS, or Azure.

## 📁 Project Structure

```text
D:\Fake-News-Detection\
├── backend/            # FastAPI Backend
│   ├── api/            # API Routes
│   ├── core/           # Configuration and Logger
│   ├── models/         # Pydantic Schemas
│   ├── services/       # RAG Pipeline, Retrieval, and LLM Logic
│   └── main.py         # Entry point
├── frontend/           # Streamlit Web App
├── tests/              # API and Logic Tests
├── docker-compose.yml  # Orchestration
├── requirements.txt    # Unified dependencies
└── faiss_index/        # Vector Store storage
```

## 🛠️ Getting Started

### 1. Environment Variables
Create a `.env` file in the root with your keys:
```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama3-8b-8192
```

### 2. Run with Docker (Recommended)
```bash
docker-compose up --build
```
- **Frontend:** [http://localhost:8501](http://localhost:8501)
- **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Run Manually (Local)
1. Install requirements: `pip install -r requirements.txt`
2. Start Backend: `uvicorn backend.main:app --port 8000`
3. Start Frontend: `streamlit run frontend/app.py`

## 🧪 Verification
Run unit and integration tests using pytest:
```bash
pytest tests/
```

## 🚀 Deployment
This system is ready for containerized cloud deployment. Each service has its own `Dockerfile` optimized for minimal size and fast startup.
