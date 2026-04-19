import pandas as pd

ds=pd.read_csv('data/processed/movie_cleaned_data.csv')
print(ds.columns)


def col_for_emotional_analysis(row):
    parts=[]
    if pd.notnull(row['title']):
        parts.append(row['title'])

    if pd.notnull(row['description']):
        parts.append(row['description'])

    return ". ".join(parts)

ds['emotion_analysis']=ds.apply(col_for_emotional_analysis,axis=1)

ds.to_csv('data/processed/movie_columns_modified.csv', index=False)
