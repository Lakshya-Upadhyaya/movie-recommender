import pandas as pd
import copy
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model=HuggingFaceEmbeddings(model_name='intfloat/e5-large')

ds=pd.read_csv('movie_columns_with_sentiments.csv')

texts=ds['embedding_text'].fillna('').tolist()

splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)

all_chunks=[]
all_metadata=[]

for i,text in enumerate(texts):
    if not text.strip():
        continue

    chunks = splitter.split_text(text)
    meta = {
        "title": ds.loc[i, "title"],
        "description": ds.loc[i, "description"],
        "directed_by": ds.loc[i, "directed_by"],
        "produced_by": ds.loc[i, "produced_by"],
        "starring": ds.loc[i, "starring"],
        "release_date": ds.loc[i, "release_date"],
        "country": ds.loc[i, "country"],
        "language": ds.loc[i, "language"],
        "main_sentiment": ds.loc[i, "main_sentiment"],
        "main_sentiment_score": ds.loc[i, "main_sentiment_score"],
        "all_sentiments": ds.loc[i, "all_sentiments"],
    }

    all_chunks.extend(chunks)
    all_metadata.extend([copy.deepcopy(meta) for _ in range(len(chunks))])

vector_db = Chroma.from_texts(all_chunks, embedding_model, metadatas=all_metadata,persist_directory="vector_db")
