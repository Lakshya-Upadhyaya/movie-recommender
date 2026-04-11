!pip install -q transformers accelerate bitsandbytes langchain_huggingface langchain_chroma chromadb nest-asyncio uvicorn fastapi pyngrok

from langchain.prompts import PromptTemplate
from huggingface_hub import login
import json, re
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings,HuggingFacePipeline
from langchain_chroma import Chroma
from transformers import pipeline,AutoModelForCausalLM,AutoTokenizer,BitsAndBytesConfig
import torch
from fastapi import FastAPI
from pyngrok import ngrok
import nest_asyncio
import uvicorn
from pydantic import BaseModel

from google.colab import drive
drive.mount('/content/drive')
embedding_model=HuggingFaceEmbeddings(model_name='intfloat/e5-large')
vector_db = Chroma(persist_directory='/content/drive/MyDrive/vector_db', embedding_function=embedding_model)

login("HuggingFace AuthToken")
model_id="mistralai/Mistral-7B-Instruct-v0.1"
tokenizer=AutoTokenizer.from_pretrained(model_id)
bnb_config = BitsAndBytesConfig(load_in_4bit=True)
model=AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map='auto',
    quantization_config=bnb_config,
    torch_dtype=torch.float16
)

pipe=pipeline("text-generation",model=model,tokenizer=tokenizer,max_new_tokens=800,device_map='auto')
llm=HuggingFacePipeline(pipeline=pipe)
parser = StrOutputParser()

emotion_model = pipeline("text-classification", model="samlowe/roberta-base-go_emotions", top_k=None)

movie_query_prompt = PromptTemplate.from_template("""
Extract structured metadata from the following movie-related user query. Your ONLY output must be a valid JSON object in the exact format shown below.

Supported Metadata:
- actor: list of actor names explicitly mentioned in the query, or null.
- director: director name explicitly mentioned, or null.
- produced_by: producer name explicitly mentioned, or null.
- year_range: list of integers representing valid years (2024 to 2027 only) explicitly mentioned in the query using year-related phrases. If no valid years mentioned, set to null.

Allowed year_range interpretations:
- "before 2025" → [2024, 2025]
- "after 2025" → [2026, 2027]
- "between 2025 and 2027" → [2025, 2026, 2027]
- "2025" → [2025]
- "2020s" → [2024, 2025, 2026, 2027]

CLEANED QUERY RULES:
- The cleaned_query is for similarity search against movie titles and descriptions.
- You MUST remove:
  - Generic request phrases: suggest, show, recommend, find, tell me, give me, upcoming, movies, movie, film, films, list of, looking for, releasing, release, new, etc.
  - Numeric years or year-related phrases (these go into year_range).
  - Structural phrases like: "released in", "directed by", "produced by", "movie directed by", "film produced by", etc.
  - Any leftover phrases like "movie releasing", "films releasing", "new movie", etc.
- You MAY retain:
  - Genres (e.g., action, comedy, thriller, sci-fi)
  - Themes or keywords (e.g., superhero, romantic comedy, detective, space adventure)
  - Explicit actor/actress names if mentioned (these can appear in similarity search)
  - Character names or fictional universes if present.
- If no meaningful keywords remain after cleaning, set cleaned_query to null.
- Do not guess or infer information not explicitly present in the query.

EXAMPLES:

---
**EXAMPLE 1 — Generic phrases removed, no keywords left**

Query: "Suggest a movie releasing in 2026"
JSON Output:
{{
  "is_movie_query": true,
  "cleaned_query": null,
  "metadata_filters": {{
    "actor": null,
    "director": null,
    "produced_by": null,
    "year_range": [2026]
  }},
  "follow_up": null
}}

---
**EXAMPLE 2 — Year-related phrase handled, actor retained in cleaned_query**

Query: "Find action movies starring Tom Cruise releasing after 2025"
JSON Output:
{{
  "is_movie_query": true,
  "cleaned_query": "action Tom Cruise",
  "metadata_filters": {{
    "actor": ["Tom Cruise"],
    "director": null,
    "produced_by": null,
    "year_range": [2026, 2027]
  }},
  "follow_up": null
}}

---
**EXAMPLE 3 — Structural phrases removed, genre retained**

Query: "I'm looking for a comedy movie directed by Wes Anderson"
JSON Output:
{{
  "is_movie_query": true,
  "cleaned_query": "comedy",
  "metadata_filters": {{
    "actor": null,
    "director": "Wes Anderson",
    "produced_by": null,
    "year_range": null
  }},
  "follow_up": null
}}

---
**EXAMPLE 4 — Complex year phrase handled, no keywords left**

Query: "List of films produced by Christopher Nolan between 2025 and 2027"
JSON Output:
{{
  "is_movie_query": true,
  "cleaned_query": null,
  "metadata_filters": {{
    "actor": null,
    "director": null,
    "produced_by": "Christopher Nolan",
    "year_range": [2025, 2026, 2027]
  }},
  "follow_up": null
}}

---
**EXAMPLE 5 — Theme retained, generic phrases and year removed**

Query: "Tell me about upcoming superhero movies from the 2020s"
JSON Output:
{{
  "is_movie_query": true,
  "cleaned_query": "superhero",
  "metadata_filters": {{
    "actor": null,
    "director": null,
    "produced_by": null,
    "year_range": [2024, 2025, 2026, 2027]
  }},
  "follow_up": null
}}

---
**EXAMPLE 6 — Actor and genre both retained**

Query: "Recommend sci-fi movies with Scarlett Johansson"
JSON Output:
{{
  "is_movie_query": true,
  "cleaned_query": "sci-fi Scarlett Johansson",
  "metadata_filters": {{
    "actor": ["Scarlett Johansson"],
    "director": null,
    "produced_by": null,
    "year_range": null
  }},
  "follow_up": null
}}

---
**EXAMPLE 7 — No useful information, query ignored**

Query: "How are you?"
JSON Output:
{{
  "is_movie_query": false,
  "cleaned_query": null,
  "metadata_filters": {{
    "actor": null,
    "director": null,
    "produced_by": null,
    "year_range": null
  }},
  "follow_up": null
}}

---

The ONLY valid output is the following JSON structure, with no explanations or additional text:

{{
  "is_movie_query": boolean,
  "cleaned_query": string or null,
  "metadata_filters": {{
    "actor": list of strings or null,
    "director": string or null,
    "produced_by": string or null,
    "year_range": list of integers or null
  }},
  "follow_up": string or null
}}

Query: {query}
JSON Output:
""")

def process_user_input(user_query: str):
    prompt = movie_query_prompt.format(query=user_query)
    output = pipe(prompt, return_full_text=False)[0]["generated_text"]

    try:
        json_match = re.search(r'\{.*\}', output, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON block found in output")

        json_str = json_match.group(0)
        data = json.loads(json_str)
        return data["cleaned_query"], data["metadata_filters"]

    except Exception as e:
        print("Error parsing:", e)
        return None, None

def query_sentiment(query):
  emotions = emotion_model(query)[0]
  main = max(emotions, key=lambda x: x["score"])
  target_sentiment = main["label"].lower()
  target_score = main["score"]
  return target_sentiment,target_score

def filter_by_metadata(results, filters):
    filtered = []

    for doc in results:
        meta = doc.metadata

        actors_filter = filters.get("actor")
        if actors_filter:
            starring = meta.get("starring", "").lower()
            if not all(actor.lower() in starring for actor in actors_filter):
                continue

        if filters.get("director"):
            if filters["director"].lower() not in meta.get("directed_by", "").lower():
                continue


        if filters.get("produced_by"):
            user_prod = filters["produced_by"].lower()
            prod = meta.get("produced_by", "").lower()
            if user_prod not in prod:
                continue


        year_filter = filters.get("year_range")
        if year_filter:
            release_date = meta.get("release_date", "")
            year_match = re.search(r'(\d{4})$', release_date)
            if not year_match:
                continue
            release_year = int(year_match.group(1))
            if release_year not in year_filter:
                continue

        filtered.append(doc)
    seen, deduped = set(), []
    for doc in filtered:
        title = doc.metadata.get("title", "").strip()
        if title and title not in seen:
            seen.add(title)
            deduped.append(doc)

    return deduped

def rank_by_emotion(results, target_sentiment, target_score):
    def closeness(doc):
        raw = doc.metadata.get("all_sentiments", {})
        if isinstance(raw, str):
            try: raw = json.loads(raw)
            except: return 1.0
        scores = {d["label"].lower(): d["score"] for d in raw if isinstance(d, dict)}
        return abs(scores.get(target_sentiment, 0.0) - target_score)
    return sorted(results, key=closeness)

output_prompt = PromptTemplate.from_template("""
You are a STRICT but friendly movie assistant.

Below is a JSON array of movie recommendations. Your job is to convert this into clean, human-readable text with consistent formatting like this:

---

Based on your request, here are some movie suggestions you might like:

-----------

Title: Movie Title
Release Date: Release Date
Description: Movie Description
Starring: Actor Names
Directed by: Director Name
Produced by: Producer Names

-----------

Repeat the same structure for all movie suggestions.

DO NOT:
- Guess or skip details
- Add summaries or opinions
- Modify the structure
- Forget to add the separator lines (-----------) between movie suggestions

Input Movie List (JSON):
{filtered_movies}

FINAL RESPONSE:
""")

def generate_output_response(cleaned_query: str, ranked):
    top_3_movies = ranked[:3] if len(ranked) > 3 else ranked
    if top_3_movies:
        filtered_movies = [
            {
                "title": doc.metadata.get("title", "Unknown Title"),
                "description": doc.metadata.get("description", "Unknown Description"),
                "release_date": doc.metadata.get("release_date", "Unknown Date"),
                "starring": doc.metadata.get("starring", "Unknown Cast"),
                "directed_by": doc.metadata.get("directed_by", "Unknown Director"),
                "produced_by": doc.metadata.get("produced_by", "Unknown Producer")
            }
            for doc in top_3_movies
        ]
        filtered_movies_json = json.dumps(filtered_movies, indent=2)
    else:
        filtered_movies_json = "[]"

    prompt = output_prompt.format(filtered_movies=filtered_movies_json)
    output = pipe(prompt, return_full_text=False)[0]["generated_text"]

    return output

def full_query_pipeline(raw_user_query):
    cleaned_query, filters = process_user_input(raw_user_query)
    target_sentiment, target_score = query_sentiment(raw_user_query)

    if cleaned_query:
        results = vector_db.similarity_search(cleaned_query, k=100)
    else:
        print("No valid cleaned_query. Using entire Vector DB for filtering.")
        results = vector_db.similarity_search("", k=vector_db._collection.count())

    filtered_data = filter_by_metadata(results, filters)
    ranked = rank_by_emotion(filtered_data, target_sentiment, target_score)

    response = generate_output_response(cleaned_query=cleaned_query, ranked=ranked)
    return response

app=FastAPI()

class QueryRequest(BaseModel):
  query:str

@app.post("/response")

def recommend_movie(request:QueryRequest):
  suggestions=full_query_pipeline(request.query)
  return {"response":suggestions}

!ngrok authtoken 
ngrok_tunnel = ngrok.connect(8000)
print("Public URL:", ngrok_tunnel.public_url)

nest_asyncio.apply()
uvicorn.run(app, host="0.0.0.0", port=8000)