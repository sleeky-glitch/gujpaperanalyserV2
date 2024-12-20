import streamlit as st
import json
import os
from pathlib import Path
import re
from fuzzywuzzy import fuzz

def load_json_files(base_path):
    all_news = []
    # Look for files matching the pattern day_month_page*.json
    json_files = [f for f in os.listdir(base_path) 
                 if f.endswith('.json') and re.match(r'^\d{1,2}_\d{1,2}_page\d+\.json$', f)]

    for json_file in json_files:
        try:
            file_path = Path(base_path) / json_file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract date from filename (e.g., 5_12_page1.json -> 05/12/2024)
            date_match = re.match(r'(\d{1,2})_(\d{1,2})_page(\d+)', json_file)
            if date_match:
                day, month, page_num = date_match.groups()
                date = f"{day.zfill(2)}/{month.zfill(2)}/2024"
            else:
                date = "Unknown Date"
                page_num = '0'

            # Process publication details
            if 'publication_details' in data:
                pub_details = data['publication_details']
                news_item = {
                    'type': 'publication_info',
                    'title': 'Publication Details',
                    'newspaper_name': pub_details.get('newspaper_name', ''),
                    'date': pub_details.get('date', ''),
                    'locations': pub_details.get('locations', []),
                    'year': pub_details.get('year', ''),
                    'issue_number': pub_details.get('issue_number', ''),
                    'page': page_num
                }
                all_news.append(news_item)

            # Process main news
            if 'main_news' in data:
                for news in data['main_news']:
                    news_item = {
                        'type': 'main_news',
                        'title': news['title'],
                        'location': news.get('location', ''),
                        'date': news.get('date', date),
                        'summary': news['details'].get('summary', '') if 'details' in news else '',
                        'key_points': news['details'].get('key_points', []) if 'details' in news else [],
                        'impact': news['details'].get('impact', []) if 'details' in news else [],
                        'additional_details': news['details'].get('additional_details', []) if 'details' in news else [],
                        'industry_reactions': news['details'].get('industry_reactions', []) if 'details' in news else [],
                        'page': page_num
                    }
                    all_news.append(news_item)

            # Process other headlines
            if 'other_headlines' in data:
                for headline in data['other_headlines']:
                    news_item = {
                        'type': 'other_headline',
                        'title': headline['title'],
                        'details': headline.get('details', []),
                        'event_details': headline.get('event_details', {}),
                        'products_displayed': headline.get('products_displayed', []),
                        'special_notes': headline.get('special_notes', []),
                        'date': date,
                        'page': page_num
                    }
                    all_news.append(news_item)

            # Process advertisements
            if 'advertisements' in data:
                for ad in data['advertisements']:
                    news_item = {
                        'type': 'advertisement',
                        'title': f"Advertisement: {ad.get('company', 'Unknown Company')}",
                        'company': ad.get('company', ''),
                        'products': ad.get('products', []),
                        'packaging': ad.get('packaging', []),
                        'contact': ad.get('contact', {}),
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
        # Check similarity with title and all other relevant fields
        title_ratio = fuzz.partial_ratio(search_term.lower(), str(news['title']).lower())

        # Create a combined text of all details for searching
        details_text = ""
        if 'summary' in news:
            details_text += str(news['summary']) + " "
        if 'key_points' in news:
            details_text += " ".join(str(point) for point in news['key_points']) + " "
        if 'impact' in news:
            details_text += " ".join(str(impact) for impact in news['impact']) + " "
        if 'details' in news:
            details_text += " ".join(str(detail) for detail in news['details']) + " "

        details_ratio = fuzz.partial_ratio(search_term.lower(), details_text.lower())

        if title_ratio >= similarity_threshold or details_ratio >= similarity_threshold:
            results.append({
                'news': news,
                'similarity': max(title_ratio, details_ratio)
            })

    results.sort(key=lambda x: x['similarity'], reverse=True)
    return results

def display_news_item(news):
    """Helper function to display news items with proper formatting"""
    st.write(f"**Type:** {news['type']}")
    st.write(f"**Date:** {news['date']}")
    st.write(f"**Page:** {news['page']}")

    if news['type'] == 'main_news':
        if 'location' in news and news['location']:
            st.write(f"**Location:** {news['location']}")
        if 'summary' in news and news['summary']:
            st.write(f"**Summary:** {news['summary']}")
        if 'key_points' in news and news['key_points']:
            st.write("**Key Points:**")
            for point in news['key_points']:
                st.write(f"- {point}")
        if 'impact' in news and news['impact']:
            st.write("**Impact:**")
            for impact in news['impact']:
                st.write(f"- {impact}")
        if 'additional_details' in news and news['additional_details']:
            st.write("**Additional Details:**")
            for detail in news['additional_details']:
                st.write(f"- {detail}")

    elif news['type'] == 'other_headline':
        if 'event_details' in news and news['event_details']:
            st.write("**Event Details:**")
            for key, value in news['event_details'].items():
                st.write(f"- {key}: {value}")
        if 'products_displayed' in news and news['products_displayed']:
            st.write("**Products Displayed:**")
            for product in news['products_displayed']:
                st.write(f"- {product}")

    elif news['type'] == 'advertisement':
        if 'company' in news:
            st.write(f"**Company:** {news['company']}")
        if 'products' in news and news['products']:
            st.write("**Products:**")
            for product in news['products']:
                st.write(f"- {product}")
        if 'contact' in news and news['contact']:
            st.write("**Contact Information:**")
            st.json(news['contact'])

def main():
    st.title("ગુજરાત સમાચાર Search")

    try:
        # Use the current directory as base path
        base_path = "."
        all_news = load_json_files(base_path)
        st.info(f"Loaded {len(all_news)} news items")

        search_term = st.text_input("Enter search term:")
        similarity_threshold = st.slider("Similarity Threshold", 0, 100, 60)

        if search_term:
            results = search_news(all_news, search_term, similarity_threshold)

            if results:
                st.write(f"Found {len(results)} relevant items:")
                for result in results:
                    news = result['news']
                    similarity = result['similarity']

                    with st.expander(f"{news['title']} (Similarity: {similarity}%)"):
                        display_news_item(news)
            else:
                st.write("No matching items found.")

    except Exception as e:
        st.error(f"Error loading news data: {str(e)}")

if __name__ == "__main__":
    main()
