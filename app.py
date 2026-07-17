import streamlit as st
import asyncio
import os
from scraper import scrapping
from recommender import load_recommender, recommend
from random_recommendation import get_combined_data, get_random_recommendations

st.set_page_config(
    page_title="AI Product Recommendations",
    layout="wide"
)


try:
    df_stats = get_combined_data()
    total_products = len(df_stats) if not df_stats.empty else 0
    total_categories = len([f for f in os.listdir("data") if f.endswith(".csv")]) if os.path.exists("data") else 0
except Exception:
    total_products = 0
    total_categories = 0


if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

with st.sidebar:
    st.title("🧭 Navigation")
    
    home_active = st.session_state.page == "🏠 Home"
    search_active = st.session_state.page == "🔍 Search"
    
    if st.button("🏠 Home", use_container_width=True, type="primary" if home_active else "secondary"):
        st.session_state.page = "🏠 Home"
        st.rerun()
        
    if st.button("🔍 Search & Scrape", use_container_width=True, type="primary" if search_active else "secondary"):
        st.session_state.page = "🔍 Search"
        st.rerun()
        
    st.divider()
    
    st.subheader("📊 Database Status")
    st.metric("Total Scraped Items", total_products)
    st.metric("Scraped Categories", total_categories)
    
    st.divider()
    st.info("💡 Tip: Go to Search to scrape fresh products from eBay and get real-time recommendations!")

st.title("🛒 AI Product Recommendations")

if st.session_state.page == "🏠 Home":
    st.subheader("Discover Random Products & Similar Recommendations")
    with st.spinner("Finding a random product and calculating recommendations..."):
        try:
            target_product, recommendations = get_random_recommendations(top_n=5)
                
            if target_product:
                if recommendations:
                    st.subheader("🌟 Top Recommendations")
                    for item in recommendations:
                        with st.container(border=True):
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                img_url = item['Image'] if item['Image'] else 'https://via.placeholder.com/130'
                                st.image(img_url, use_container_width=True)
                            with col2:
                                st.subheader(item['Title'])
                                c1, c2, c3 = st.columns(3)
                                c1.metric("Price", item['Price'])
                                condition_val = item['Condition'].strip() if (isinstance(item['Condition'], str) and item['Condition'].strip()) else "Not Specified"
                                c2.metric("Condition", condition_val)
                                c3.metric("Similarity", f"{item['Similarity']}%")
                                st.link_button("View & Buy on eBay", item['URL'], type="primary")
                else:
                    st.warning("No Recommendations.")
            else:
                st.info("No scraped datasets found. Please search for a product in the search tab first to scrape data!")
        except Exception as e:
            st.error(f"Error generating random recommendation: {e}")

elif st.session_state.page == "🔍 Search":
    st.subheader("Search Live Listings & Get Similar Recommendations")
    query = st.text_input("Enter Product Name", key="search_query")
    
    if st.button("Recommend", key="btn_recommend"):
        if query.strip():
            with st.spinner("Scraping live listings and calculating recommendations..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    scrapping(query)
                    load_recommender(query)
                    recommendations = recommend(query)
                    
                    if recommendations:
                        st.success("Top 5 Recommendations:")
                        for item in recommendations:
                            
                            with st.container(border=True):
                                col1, col2 = st.columns([1, 4])
                                with col1:
                                    img_url = item['Image'] if item['Image'] else 'https://via.placeholder.com/130'
                                    st.image(img_url, use_container_width=True)
                                with col2:
                                    st.subheader(item['Title'])
                                    c1, c2, c3 = st.columns(3)
                                    c1.metric("Price", item['Price'])
                                    condition_val = item['Condition'].strip() if (isinstance(item['Condition'], str) and item['Condition'].strip()) else "Not Specified"
                                    c2.metric("Condition", condition_val)
                                    c3.metric("Similarity", f"{item['Similarity']}%")
                                    st.link_button("View & Buy on eBay", item['URL'], type="primary")
                    else:
                        st.error("No recommendations found.")
                        
                except Exception as e:
                    st.error(f"Error during recommendation process: {e}")
        else:
            st.warning("Please enter a product name first.")

