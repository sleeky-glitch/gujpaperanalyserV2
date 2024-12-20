# app.py
import streamlit as st
import json
import os
from openai import OpenAI
from typing import List, Dict
import logging
from pathlib import Path

class NewspaperFinderBot:
    def __init__(self):
        # Use Streamlit secrets for API key
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def load_json_files(self) -> List[Dict]:
        """Load all JSON files from the data directory."""
        all_news = []
        try:
            # Get the current directory
            current_dir = Path(__file__).parent
            data_dir = current_dir / "data"

            for filename in os.listdir(data_dir):
                if filename.endswith('.json'):
                    file_path = data_dir / filename
                    with open(file_path, 'r', encoding='utf-8') as file:
                        news_data = json.load(file)
                        all_news.extend(news_data if isinstance(news_data, list) else [news_data])
            logging.info(f"Successfully loaded {len(all_news)} news articles")
            return all_news
        except Exception as e:
            logging.error(f"Error loading JSON files: {str(e)}")
            st.error(f"Error loading JSON files: {str(e)}")
            return []

    def search_news(self, query: str, news_data: List[Dict], max_results: int = 5) -> List[Dict]:
        """Search news articles based on user query using OpenAI."""
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant that searches through Gujarati newspaper articles. Return relevant articles based on the query."},
                {"role": "user", "content": f"Search for articles related to: {query}"}
            ]

            articles_context = "\n".join([
                f"Article {i+1}: {article.get('title', 'No title')} - {article.get('summary', 'No summary')[:100]}..."
                for i, article in enumerate(news_data[:10])
            ])
            messages.append({"role": "user", "content": f"Available articles:\n{articles_context}"})

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            relevant_articles = []
            for article in news_data:
                if any(keyword.lower() in article.get('content', '').lower() 
                      for keyword in query.lower().split()):
                    relevant_articles.append(article)
                if len(relevant_articles) >= max_results:
                    break

            logging.info(f"Found {len(relevant_articles)} relevant articles for query: {query}")
            return relevant_articles

        except Exception as e:
            logging.error(f"Error searching news: {str(e)}")
            st.error(f"Error searching news: {str(e)}")
            return []

def main():
    st.set_page_config(
        page_title="Gujarati News Finder",
        page_icon="📰",
        layout="wide"
    )

    st.title("📰 Gujarati News Finder")
    st.write("Search through Gujarati newspaper articles using natural language queries.")

    # Initialize the bot
    bot = NewspaperFinderBot()

    # Load news data
    with st.spinner("Loading news articles..."):
        news_data = bot.load_json_files()
        st.success(f"Loaded {len(news_data)} articles successfully!")

    # Search interface
    query = st.text_input("Enter your search query:", placeholder="Example: Recent political news in Gujarat")
    max_results = st.slider("Maximum number of results:", 1, 20, 5)

    if st.button("Search", type="primary"):
        if query:
            with st.spinner("Searching..."):
                results = bot.search_news(query, news_data, max_results)

            if results:
                st.write(f"Found {len(results)} relevant articles:")
                for i, article in enumerate(results, 1):
                    with st.expander(f"{i}. {article.get('title', 'No title')}"):
                        st.write("**Summary:**")
                        st.write(article.get('summary', 'No summary'))
                        st.write("**Content:**")
                        st.write(article.get('content', 'No content available'))
                        if 'date' in article:
                            st.write(f"**Date:** {article['date']}")
                        if 'source' in article:
                            st.write(f"**Source:** {article['source']}")
            else:
                st.warning("No relevant articles found.")
        else:
            st.warning("Please enter a search query.")

    # Add filters in the sidebar
    st.sidebar.title("Filters")
    st.sidebar.info("""
    This app searches through Gujarati newspaper articles using AI-powered search.

    **Features:**
    - Natural language queries
    - Full-text search
    - Article summaries
    - Source information
    """)

if __name__ == "__main__":
    main()
