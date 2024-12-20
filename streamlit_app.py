import streamlit as st
import json
import os
from pathlib import Path
import re
from fuzzywuzzy import fuzz

def load_json_files(base_path):
    all_news = []
    # Get all folders matching the pattern d_dd or dd_dd
    date_folders = [f for f in os.listdir(base_path) 
                   if os.path.isdir(os.path.join(base_path, f)) 
                   and re.match(r'^\d{1,2}_\d{1,2}$', f)]

    for date_folder in date_folders:
        folder_path = Path(base_path) / date_folder
        # Process each page.json file in the date folder
        for json_file in folder_path.glob('page*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Extract date from the folder name
                    day, month = date_folder.split('_')
                    # Pad day and month with leading zeros if needed
                    date = f"{day.zfill(2)}/{month.zfill(2)}/2024"

                    # Get page number from filename
                    page_match = re.search(r'page(\d+)', json_file.name)
                    page_num = page_match.group(1) if page_match else '0'

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
        # Check similarity with title and details
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

    # Use current directory as default if no path is provided
    default_path = os.getcwd()
    base_path = st.text_input("Enter the path to your news folders:", value=default_path)

    if base_path:
        try:
            # Load all news data
            all_news = load_json_files(base_path)
            st.info(f"Loaded {len(all_news)} news items from {base_path}")

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

        except Exception as e:
            st.error(f"Error loading news data: {str(e)}")

if __name__ == "__main__":
    main()