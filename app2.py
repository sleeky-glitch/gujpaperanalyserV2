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
        text_files = glob.glob("data/*.txt")
        return text_files
    except Exception as e:
        st.error(f"Error reading directory: {str(e)}")
        return []

def search_in_files(search_word):
    all_results = []
    text_files = get_all_text_files()

    if not text_files:
        st.warning("No text files found in the data directory")
        return []

    for file_path in text_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                articles = content.split('\n')

                for article in articles:
                    if search_word.lower() in article.lower():
                        file_name = os.path.basename(file_path)
                        all_results.append({
                            'file': file_name,
                            'content': article
                        })

        except Exception as e:
            st.error(f"Error reading {file_path}: {str(e)}")
            continue

    return all_results

def display_results(results):
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

def main():
    st.title("Gujarati News Search")
    st.write("Search for news articles in Gujarati")

    # Display available text files
    text_files = get_all_text_files()
    if text_files:
        with st.expander("Available Text Files"):
            for file in text_files:
                st.write(f"📄 {os.path.basename(file)}")
    else:
        st.warning("No text files found in the data directory")
        return

    # Add radio button for search type
    search_type = st.radio(
        "Choose search method:",
        ["English to Gujarati", "Direct Gujarati Input"],
        horizontal=True
    )

    if search_type == "English to Gujarati":
        search_word = st.text_input("Enter a word to search (in English):")

        if search_word:
            with st.spinner("Translating..."):
                gujarati_word = translate_to_gujarati(search_word)

            if gujarati_word:
                st.success(f"Translated word: {gujarati_word}")

                if st.button("Search", key="english_search"):
                    with st.spinner("Searching in all files..."):
                        results = search_in_files(gujarati_word)
                        display_results(results)

    else:  # Direct Gujarati Input
        # Add a helper message for typing in Gujarati
        st.markdown("""
        💡 **Tip:** To type in Gujarati:
        - Use Google Translate keyboard
        - Use Windows Gujarati keyboard
        - Copy and paste Gujarati text
        """)

        gujarati_word = st.text_input("Enter text in Gujarati:", key="gujarati_input")

        if gujarati_word:
            if st.button("Search", key="gujarati_search"):
                with st.spinner("Searching in all files..."):
                    results = search_in_files(gujarati_word)
                    display_results(results)

    # Add footer with instructions
    st.markdown("---")
    st.markdown("""
    **Instructions:**
    1. Choose your search method:
       - English to Gujarati: Enter English word for automatic translation
       - Direct Gujarati Input: Type or paste Gujarati text directly
    2. Enter your search term
    3. Click 'Search' to find related news articles
    4. Click on each file to view the matching articles
    """)

    # Add information about keyboard support
    with st.expander("ℹ️ How to type in Gujarati"):
        st.markdown("""
        **Options for typing in Gujarati:**
        1. **Google Input Tools:**
           - Visit [Google Input Tools](https://www.google.com/inputtools/try/)
           - Select Gujarati
           - Type and copy the text

        2. **Windows Gujarati Keyboard:**
           - Go to Windows Settings > Time & Language > Language
           - Add Gujarati as a language
           - Use the language bar to switch to Gujarati keyboard

        3. **Mobile Device:**
           - Install Gujarati keyboard from your app store
           - Switch to Gujarati input method
           - Type and share/copy the text

        4. **Copy & Paste:**
           - Use any online Gujarati typing tool
           - Copy the text and paste it here
        """)

if __name__ == "__main__":
    main()

# Created/Modified files during execution:
# None (this script only reads from existing files)
