import streamlit as st
import json
import glob
import os
from googletrans import Translator
from datetime import datetime

def load_json_files():
    """Load all JSON files from the root directory"""
    json_files = glob.glob("*.json")
    all_data = {}
    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                # Extract date from filename (assuming format: YYYY-MM-DD-pageX.json)
                date_str = file.split('-')[0:3]
                date = '-'.join(date_str)
                data = json.load(f)
                all_data[date] = data
        except Exception as e:
            st.error(f"Error loading {file}: {str(e)}")
    return all_data

def translate_text(text, target_lang='gu'):
    """Translate text between English and Gujarati"""
    translator = Translator()
    try:
        translation = translator.translate(text, dest=target_lang)
        return translation.text
    except:
        return text

def search_news(data, search_term):
    """Search for news containing the search term in both English and Gujarati"""
    results = []

    # Translate search term to both languages
    guj_term = translate_text(search_term, 'gu') if search_term.isascii() else search_term
    eng_term = translate_text(search_term, 'en') if not search_term.isascii() else search_term

    search_terms = [search_term.lower(), guj_term.lower(), eng_term.lower()]

    for date, content in data.items():
        # Search in main news
        for news in content.get('main_news', []):
            for term in search_terms:
                if (term in news.get('title', '').lower() or 
                    term in str(news.get('details', '')).lower()):
                    results.append({
                        'date': date,
                        'title': news['title'],
                        'details': news['details'].get('summary', '') if isinstance(news['details'], dict) else str(news['details'])
                    })
                    break

        # Search in other headlines
        for headline in content.get('other_headlines', []):
            for term in search_terms:
                if (term in headline.get('title', '').lower() or 
                    term in str(headline.get('details', '')).lower()):
                    results.append({
                        'date': date,
                        'title': headline['title'],
                        'details': str(headline.get('details', ''))
                    })
                    break

    return results

def main():
    st.title("ગુજરાતી સમાચાર શોધક / Gujarati News Finder")

    # Load data
    data = load_json_files()

    # Search interface
    search_term = st.text_input("Enter search term (English or Gujarati):")

    if search_term:
        results = search_news(data, search_term)

        if results:
            st.success(f"Found {len(results)} results")
            for result in results:
                with st.expander(f"{result['date']} - {result['title']}"):
                    st.write(result['details'])
        else:
            st.warning("No results found")

if __name__ == "__main__":
    main()

# Created/Modified files during execution:
# No files are created or modified during execution
