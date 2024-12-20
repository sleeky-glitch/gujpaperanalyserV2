import streamlit as st
import json
import os
from pathlib import Path
import re
from fuzzywuzzy import fuzz

def load_json_files(base_path):
    all_news = []
    # Walk through all date folders
    for date_folder in os.listdir(base_path):
        folder_path = Path(base_path) / date_folder
        if folder_path.is_dir():
            # Process each page.json file in the date folder
            for json_file in folder_path.glob('page*.json'):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                        # Extract date from the folder name (assuming format like "5_12")
                        day, month = date_folder.split('_')
                        date = f"{day}/{month}/2024"

                        # Get page number from filename
                        page_num = re.search(r'page(\d+)', json_file.name).group(1)

                        # Process main news
                        if 'main_news' in data:
                            for news in data['main_news']:
                                news_item = {
                                    'title': news['title'],
                                    'details': news['details']['summary'] if 'details' in news and 'summary' in news['details'] else '',
                                    'date': date,
                                    'page': page_num
                                }
                                all_news.append(news_item)

                        # Process other headlines
                        if 'other_headlines' in data:
                            for headline in data['other_headlines']:
                                news_item = {
                                    'title': headline['title'],
                                    'details': headline.get('details', ''),
                                    'date': date,
                                    'page': page_num
                                }
                                all_news.append(news_item)

                except Exception as e:
                    st.error(f"Error processing {json_file}: {str(e)}")

    return all_news

def search_news(news_list, search_term, similarity_threshold=60):
    results = []
    for news in news_list:
        # Check similarity with title
        title_ratio = fuzz.partial_ratio(search_term.lower(), news['title'].lower())
        details_ratio = fuzz.partial_ratio(search_term.lower(), str(news['details']).lower())

        if title_ratio >= similarity_threshold or details_ratio >= similarity_threshold:
            results.append({
                'news': news,
                'similarity': max(title_ratio, details_ratio)
            })

    # Sort results by similarity score
    results.sort(key=lambda x: x['similarity'], reverse=True)
    return results

def main():
    st.title("ગુજરાત સમાચાર Search")

    # Input for base directory path
    base_path = st.text_input("Enter the path to your news folders:", "")

    if base_path:
        # Load all news data
        all_news = load_json_files(base_path)

        # Search interface
        search_term = st.text_input("Enter search term:")
        similarity_threshold = st.slider("Similarity Threshold", 0, 100, 60)

        if search_term:
            results = search_news(all_news, search_term, similarity_threshold)

            if results:
                st.write(f"Found {len(results)} relevant news items:")
                for result in results:
                    news = result['news']
                    similarity = result['similarity']

                    with st.expander(f"{news['title']} (Similarity: {similarity}%)"):
                        st.write(f"**Date:** {news['date']}")
                        st.write(f"**Page:** {news['page']}")
                        st.write(f"**Details:** {news['details']}")
            else:
                st.write("No matching news found.")

if __name__ == "__main__":
    main()

# Required packages:
# pip install streamlit fuzzywuzzy python-Levenshtein
