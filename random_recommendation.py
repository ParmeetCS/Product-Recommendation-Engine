from requests import request
import pandas as pd
import os
from pathlib import Path
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import os

def get_combined_data():
    """
    Loads all CSV files from the 'data' directory and combines them into one DataFrame.
    """
    folder = Path("data")
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
        return pd.DataFrame()
    
    dfs = []
    for file in folder.iterdir():
        if file.is_file() and file.suffix == ".csv":
            try:
                temp_df = pd.read_csv(file)
                if not temp_df.empty:
                    dfs.append(temp_df)
            except Exception as e:
                print(f"Error reading {file}: {e}")
                
    if not dfs:
        return pd.DataFrame()
        
    combined_df = pd.concat(dfs, ignore_index=True)
    
    combined_df = combined_df.drop_duplicates(subset=["Title", "URL"], keep="first").reset_index(drop=True)
    return combined_df

def clean_text(text):
    text = str(text)
    
    text = text.replace("Opens in a new window or tab", "")
    text = text.replace("New Listing", "")

    for char in [",", "-", "|", "[", "]", "(", ")", "*", "/", "+", ":", "or tab"]:
        text = text.replace(char, " ")
    return " ".join(text.split()).strip()

def get_random_recommendations(top_n=5):
    """
    Selects a random product from all combined recent scraped data
    and generates top_n recommendations based on TF-IDF cosine similarity.
    
    Returns:
        tuple: (dict of selected target random product, list of dicts of recommended products)
        or (None, None) if not enough data is available.
    """
    df = get_combined_data()
    if df.empty:
        return None, None
        

    df['Title'] = df['Title'].fillna("")
    df['Condition'] = df['Condition'].fillna("")
    df['Price'] = df['Price'].fillna("")
    df['Image'] = df['Image'].fillna("")
    df['URL'] = df['URL'].fillna("")
    
    df['CleanTitle'] = df['Title'].apply(clean_text)
    df['CleanCondition'] = df['Condition'].apply(clean_text)
    
   
    df['Features'] = df['CleanTitle'] + " " + df['CleanCondition']
   
    random_index = random.randint(0, len(df) - 1)
    random_product = df.iloc[random_index].to_dict()
    
  
    if len(df) < 2:
        return random_product, []

    vectorizer = TfidfVectorizer(stop_words="english")
    feature_vectorized = vectorizer.fit_transform(df["Features"])
    similarity_matrix = cosine_similarity(feature_vectorized)
    
   
    similarity_scores = list(enumerate(similarity_matrix[random_index]))
    
 
    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )
    
    recommendations = []
    count = 0
    
    for index, score in similarity_scores:
     
        if index == random_index:
            continue
            
        item_row = df.iloc[index]
        sim_percentage = round(score * 100, 1)
        
        if sim_percentage > 20:
            recommendations.append({
                "Title": item_row["Title"],
                "Price": item_row["Price"],
                "Condition": item_row["Condition"],
                "Image": item_row["Image"],
                "image": item_row["Image"],
                "URL": item_row["URL"],
                "Similarity": sim_percentage,
                "Similiarity": sim_percentage
            })
            count += 1
            if count == top_n:
                break
            
    return random_product, recommendations
