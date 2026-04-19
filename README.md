# 🎬 MovieMate — Movie Recommender Chatbot

An end-to-end movie recommendation system powered by a custom web-scraped dataset, hybrid retrieval (vector search + metadata filtering), emotion-based reranking, and a 14B parameter LLM for conversational recommendations with token streaming.

---

## UI

![App Screenshot](assets/ui_landing.png)

---

## Demo

![CineChat Demo]()

---

## Implementation

### [Project Demo Video 1]()
### [Project Demo Video 2]()
### [Project Demo Video 3]()

---

## Architecture

![Flowchart]()

---

## Pipeline

```
User Query
    ↓
LLM Query Rewriting          (Qwen2.5-14B → structured embedding format)
    ↓
Metadata Extraction          (actor / director / title / year via regex)
    ↓
Hybrid Retrieval             (pgvector similarity + SQL metadata filters)
    ↓
Emotion Reranking            (RoBERTa-based emotion similarity scoring)
    ↓
Streaming Generation         (Qwen2.5-14B via TextIteratorStreamer → SSE)
    ↓
Next.js Frontend             (token-by-token streaming UI)
```

---

## Features

- **Custom Dataset** — scraped from [Wikipedia](https://www.wikipedia.org/) using BeautifulSoup and Requests; includes titles, descriptions, cast, directors, release dates, and sentiment annotations
- **LLM Query Rewriting** — transforms freeform user queries into structured embedding-aligned format before retrieval
- **Hybrid Retrieval** — pgvector cosine similarity combined with SQL metadata filters (actor, director, title, year) via Supabase RPC
- **Emotion-Based Reranking** — RoBERTa model scores emotional similarity between query and retrieved movies, reranks candidates before generation
- **Token Streaming** — Qwen2.5-14B generates responses token-by-token via `TextIteratorStreamer`, streamed to the frontend as Server-Sent Events
- **Guardrail** — off-topic queries detected and rejected before hitting the retrieval pipeline
- **Responsive UI** — Next.js + Tailwind frontend with markdown rendering and streaming chat interface

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js, Tailwind CSS, Vercel |
| **Backend** | FastAPI, Python, ngrok |
| **LLM** | Qwen2.5-14B-Instruct (4-bit via Unsloth) |
| **Embeddings** | nomic-ai/nomic-embed-text-v1.5 |
| **Emotion Model** | samlowe/roberta-base-go_emotions |
| **Vector DB** | pgvector on Supabase |
| **Prompt Orchestration** | LangChain |
| **Data Collection** | BeautifulSoup, Requests, Wikipedia |
| **Inference Runtime** | Kaggle (dual T4 GPU) |

---

## Deployment Stack

```
Frontend    →  Vercel (Next.js)
Backend     →  Kaggle Notebooks (FastAPI + Uvicorn)
Tunnel      →  ngrok static domain
Vector DB   →  Supabase (pgvector)
```

---

## How It Works

### 1. Data Collection
Movies were scraped from Wikipedia using BeautifulSoup and Requests — one of the more involved parts of the project. Each entry includes title, description, cast, director, country, language, release date, and sentiment annotations generated via a RoBERTa emotion classifier.

### 2. Query Rewriting
Before embedding, the user query is rewritten by Qwen2.5-14B into a structured format matching how movies were embedded during ingestion:
```
"movies with the rock" → "Starring: Dwayne Johnson"
"sad romantic films"   → "Description: romance | Emotion: sadness"
```
This aligns the query and document embedding spaces for better retrieval.

### 3. Hybrid Retrieval
Metadata fields (actor, director, title, year) are extracted from the rewritten query and passed as SQL filters to Supabase. Vector similarity reranks within the filtered candidate pool — exact matches handled by SQL, semantic similarity handled by pgvector.

### 4. Emotion Reranking
Retrieved candidates are reranked by cosine similarity between the query's emotion vector and each movie's precomputed emotion vector (28-dimensional RoBERTa output).

### 5. Streaming Generation
The top 5 reranked movies are passed as context to Qwen2.5-14B, which generates a conversational recommendation streamed token-by-token to the frontend via SSE.

---

## Setup

### Prerequisites
- Kaggle account with GPU quota (dual T4)
- Supabase project with pgvector enabled
- ngrok account with a static domain
- Vercel account

### 1. Clone the repository
```bash
git clone <repo_link>
cd movie-recommender
```

### 2. Supabase Setup
- Enable pgvector extension in your Supabase project
- Run the `match_movies` RPC function from `backend/supabase_setup.sql`
- Upload your dataset embeddings to the `movies` table

### 3. Kaggle Secrets
Add the following secrets in your Kaggle notebook settings:
```
SUPABASE_URL
SUPABASE_KEY
NGROK_TOKEN
HF_TOKEN
```

### 4. Run the Inference Server
Open `backend/response-pipeline.ipynb` in Kaggle, attach GPU accelerator (2x T4), and run all cells. The ngrok URL will be printed in the output.

### 5. Frontend Setup
Set the backend URL in your Vercel project environment variables:
```
NEXT_PUBLIC_API_URL=https://your-ngrok-domain.ngrok-free.app
```
Deploy the `frontend/` directory to Vercel.

---

## Limitations

- Single-user inference (one generation at a time on Kaggle GPU)
- Backend requires manual Kaggle session start
- Dataset coverage limited to movies available on Wikipedia at scrape time

---

## Acknowledgements

- [Unsloth](https://github.com/unslothai/unsloth) for efficient 4-bit inference
- [nomic-ai](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) for the embedding model
- [Supabase](https://supabase.com) for pgvector hosting
