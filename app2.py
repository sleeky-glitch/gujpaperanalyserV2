import streamlit as st
from deep_translator import GoogleTranslator
import os

def translate_to_gujarati(word):
    try:
        translator = GoogleTranslator(source='en', target='gu')
        translation = translator.translate(word)
        return translation
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return None

def search_in_file(translated_word, file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Split content into news articles (assuming they're separated by newlines)
            articles = content.split('\n\n')  # Adjust separator based on your file format

            matching_articles = []
            for article in articles:
                if translated_word.lower() in article.lower():
                    matching_articles.append(article)

            return matching_articles
    except FileNotFoundError:
        return ["File not found. Please check the file path."]
    except Exception as e:
        return [f"An error occurred: {str(e)}"]

def main():
    st.title("Gujarati News Search")

    # Input word from user
    search_word = st.text_input("Enter a word to search (in English):")

    if search_word:
        # Translate word to Gujarati
        gujarati_word = translate_to_gujarati(search_word)

        if gujarati_word:
            st.write(f"Translated word: {gujarati_word}")

            # Specify the path to your text file
            file_path = "data/your_text_file.txt"  # Update this path

            # Search for the translated word
            if st.button("Search"):
                results = search_in_file(gujarati_word, file_path)

                if results:
                    st.subheader("Found News Articles:")
                    for idx, article in enumerate(results, 1):
                        st.write(f"Article {idx}:")
                        st.write(article)
                        st.markdown("---")
                else:
                    st.warning("No articles found containing this word.")

if __name__ == "__main__":
    main()

# Created/Modified files during execution:
# None (this script only reads from existing files)
