from numpy import result_type
from transformers import pipeline
import pandas as pd
import json
from tqdm import tqdm

tqdm.pandas()
emotion_classifier = pipeline("text-classification", model="samlowe/roberta-base-go_emotions",top_k=None)
ds=pd.read_csv('data/processed/movie_columns_modified.csv')


def sentiment_values(row):
    if pd.notnull(row):
        emotions=emotion_classifier(row)[0]
        main_label=emotions[0]['label'] 
        main_score=emotions[0]['score']
        all_emotions=(json.dumps(emotions))
        return pd.Series([main_label,main_score,all_emotions])
    else:
        return pd.Series([None,None,None])

ds[['main_sentiment','main_sentiment_score','all_sentiments']]=ds['emotion_analysis'].progress_apply(
    sentiment_values
)

ds.to_csv('data/processed/movie_columns_with_sentiments.csv',index=False)