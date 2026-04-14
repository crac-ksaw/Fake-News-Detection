# Fake News Detection API

A simplified fake news detection project with a FastAPI backend, a Streamlit frontend, live news retrieval, and Groq-based reasoning.

## Features

- FastAPI backend for API access
- Streamlit frontend for quick manual checks
- Live retrieval from public news search feeds
- Groq-powered classification over retrieved evidence
- Request and response validation with Pydantic
- Confidence threshold fallback to `UNCERTAIN`
- Console and rotating file logging
- Docker support

## Project Structure

```text
D:\Fake-News-Detection\
|-- backend/
|   |-- api/
|   |-- core/
|   |-- models/
|   |-- services/
|   `-- main.py
|-- frontend/
|-- tests/
|-- docker-compose.yml
|-- requirements.txt
`-- README.md
```

## Environment

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_key_here
```

Optional settings:

```env
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TIMEOUT_SECONDS=30
CONFIDENCE_THRESHOLD=0.70
```

Only `GROQ_API_KEY` is required.

## Local Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Start the frontend:

```bash
streamlit run frontend/app.py
```

- Backend docs: http://localhost:8000/docs
- Frontend: http://localhost:8501

## Docker Run

```bash
docker-compose up --build
```

## Tests

```bash
pytest tests/
```
