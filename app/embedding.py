import pandas as pd
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


ds = pd.read_csv('data/processed/movie_with_tagged_description.csv')

texts = ds['embedding_text'].fillna('').tolist()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

all_chunks = []
all_metadata = []

for i, text in enumerate(texts):
    chunks = splitter.split_text(text)
    meta = {
        "title": ds.loc[i, "title"],
        "description": ds.loc[i, "description"],
        "directed_by": ds.loc[i, "directed_by"],
        
    }
    all_chunks.extend(chunks)
    all_metadata.extend([meta] * len(chunks))

vector_db = Chroma.from_texts(all_chunks, embedding_model, metadatas=all_metadata, persist_directory="vector_db")
vector_db.persist()

