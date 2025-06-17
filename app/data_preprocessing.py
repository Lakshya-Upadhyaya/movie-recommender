import pandas as pd

ds=pd.read_csv('data/processed/movie_cleaned_data.csv')
print(ds.columns)
def create_movie_description(row):
    parts=[]

    if pd.notnull(row['title']):
        parts.append(f"Title: {row['title']}")

    if pd.notnull(row['description']):
        parts.append(f"Description: {row['description']}")

    if pd.notnull(row['directed_by']):
        parts.append(f"Directed by: {row['directed_by']}")

    if pd.notnull(row['produced_by']):
        parts.append(f"Produced by: {row['produced_by']}")

    if pd.notnull(row['starring']):
        parts.append(f"Starring: {row['starring']}")

    if pd.notnull(row['country']):
        parts.append(f"Country: {row['country']}")

    if pd.notnull(row['language']):
        parts.append(f"Language: {row['language']}")

    if pd.notnull(row['release_date']):
        parts.append(f"Release Date: {row['release_date']}")

    return " | ".join(parts)

def col_for_emotional_analysis(row):
    parts=[]
    if pd.notnull(row['title']):
        parts.append(row['title'])

    if pd.notnull(row['description']):
        parts.append(row['description'])

    return ". ".join(parts)

ds['emotion_analysis']=ds.apply(col_for_emotional_analysis,axis=1)
ds['embedding_text']=ds.apply(create_movie_description,axis=1)

ds.to_csv('data/processed/movie_columns_modified.csv', index=False)
