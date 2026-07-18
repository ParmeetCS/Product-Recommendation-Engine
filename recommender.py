import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def clean_text(text):
    text = str(text)
    text = text.replace("Opens in a new window or tab", "")
    text = text.replace("New Listing", "")
    for char in [",", "-", "|", "[", "]", "(", ")", "*", "/", "+", ":", "or tab"]:
        text = text.replace(char, " ")
    return " ".join(text.split()).strip()

def load_recommender(product_name=""):
    import os
    file_name = f"data/Ebay_{product_name}.csv"
    if not product_name or not os.path.exists(file_name):
        file_name = "ebay_product_list.csv"
        
    df = pd.read_csv(file_name)

    df = df.drop_duplicates(subset=["Title", "URL"], keep="first").reset_index(drop=True)
    df['CleanTitle'] = df['Title'].fillna("").apply(clean_text)
    df['CleanCondition'] = df['Condition'].fillna("").apply(clean_text)
    df['Features'] = df['CleanTitle'] + " " + df['CleanCondition']
    
    vectorizer = TfidfVectorizer(stop_words="english")
    feature_vectorized = vectorizer.fit_transform(df["Features"])
    similarity_matrix = cosine_similarity(feature_vectorized)
    return df, similarity_matrix, vectorizer

def recommend(product_name, top_n=5):
    df, similarity_matrix, vectorizer = load_recommender(product_name)
    if df.empty:
        return []

    product_name_clean = clean_text(product_name.lower().strip())
    if not product_name_clean:
        return []

    query_vector = vectorizer.transform([product_name_clean])
    feature_vectorized = vectorizer.transform(df["Features"])
    query_similarities = cosine_similarity(query_vector, feature_vectorized).flatten().tolist()
    product_index = query_similarities.index(max(query_similarities))

    similarity_scores = list(
        enumerate(similarity_matrix[product_index])
    )

    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    recommendations = []
    count = 0

    for index, score in similarity_scores:
        if index == product_index:
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

    return recommendations



