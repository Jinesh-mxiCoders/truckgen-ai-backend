# TruckGen AI Chatbot Backend

This repository contains the backend for **TruckGen AI**, a FastAPI-based chatbot for Schwing trucks. The backend is built with **Python**, managed via **Poetry**, and follows a modular architecture for maintainability, scalability, and easy integration of multiple LLM and image-generation providers.

---

## Tech Stack

- **Language:** Python
- **Web Framework:** FastAPI
- **Dependency Management:** Poetry
- **ASGI Server:** Uvicorn
- **Session Store:** Redis
- **LLM / AI:** OpenAI GPT
- **Embeddings:** Sentence Transformers (`all-mpnet-base-v2`)
- **Database:** PostgreSQL
    - **Vector Data Support:** pgvector

---

## Prerequisites

Before running the project, ensure you have:

- Python 3.11+
- Poetry >= 1.5.1
- Redis
- PostgreSQL

## Running the App

1. **Install dependencies**  
```bash
poetry install
```

2. **Activate the virtual environment**  
```bash
poetry shell
```

3. **Start application**  
```bash
python start.py
```
