import streamlit as st
from deep_translator import GoogleTranslator
import os
import glob

def translate_to_gujarati(word):
    try:
        translator = GoogleTranslator(source='en', target='gu')
        translation = translator.translate(word)
        return translation
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return None

def get_all_text_files():
    try:
        # Get all .txt files from the data directory
        text_files = glob.glob("data/*.txt")
        return text_files
    except Exception as e:
        st.error(f"Error reading directory: {str(e)}")
        return []

def search_in_files(translated_word):
    all_results = []

    # Get list of all text files
    text_files = get_all_text_files()

    if not text_files:
        st.warning("No text files found in the data directory")
        return []

    for file_path in text_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # Split content into news articles
                articles = content.split('\n\n')  # Adjust separator based on your file format

                # Find matching articles
                for article in articles:
                    if translated_word.lower() in article.lower():
                        # Store both the filename and the article content
                        file_name = os.path.basename(file_path)
                        all_results.append({
                            'file': file_name,
                            'content': article
                        })

        except Exception as e:
            st.error(f"Error reading {file_path}: {str(e)}")
            continue

    return all_results

def main():
    st.title("Gujarati News Search")

    # Add a brief description
    st.write("Enter an English word to search for related news in Gujarati across all text files.")

    # Display available text files
    text_files = get_all_text_files()
    if text_files:
        with st.expander("Available Text Files"):
            for file in text_files:
                st.write(f"📄 {os.path.basename(file)}")
    else:
        st.warning("No text files found in the data directory")
        return

    # Input word from user
    search_word = st.text_input("Enter a word to search (in English):")

    if search_word:
        # Show loading message while translating
        with st.spinner("Translating..."):
            gujarati_word = translate_to_gujarati(search_word)

        if gujarati_word:
            st.success(f"Translated word: {gujarati_word}")

            # Search for the translated word
            if st.button("Search"):
                with st.spinner("Searching in all files..."):
                    results = search_in_files(gujarati_word)

                if results:
                    st.subheader(f"Found {len(results)} News Articles:")

                    # Group results by file
                    files_dict = {}
                    for result in results:
                        if result['file'] not in files_dict:
                            files_dict[result['file']] = []
                        files_dict[result['file']].append(result['content'])

                    # Display results grouped by file
                    for file_name, articles in files_dict.items():
                        with st.expander(f"📄 {file_name} ({len(articles)} articles)"):
                            for idx, article in enumerate(articles, 1):
                                st.markdown(f"**Article {idx}:**")
                                st.write(article)
                                if idx < len(articles):
                                    st.markdown("---")
                else:
                    st.warning("No articles found containing this word.")

    # Add footer with instructions
    st.markdown("---")
    st.markdown("""
    **Instructions:**
    1. Enter an English word in the text box
    2. The word will be translated to Gujarati
    3. Click 'Search' to find related news articles in all text files
    4. Click on each file to view the matching articles
    """)

if __name__ == "__main__":
    main()

# Created/Modified files during execution:
# None (this script only reads from existing files)
