import streamlit as st
import os
from pathlib import Path
import logging
from llama_index.core import (
    VectorStoreIndex,
    Document,
    Settings
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SimpleNodeParser


class NewspaperFinderBot:
    def __init__(self):
        # Initialize OpenAI
        self.llm = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        self.embed_model = OpenAIEmbedding(api_key=st.secrets["OPENAI_API_KEY"])

        # Configure settings
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.chunk_size = 512

        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    @staticmethod
    @st.cache_resource
    def load_and_index_articles():
        """Load text files and create a searchable index."""
        try:
            # Get the current directory
            current_dir = Path(__file__).parent
            data_dir = current_dir / "data"

            documents = []
            total_articles = 0

            for filename in os.listdir(data_dir):
                if filename.endswith('.txt'):  # Process only .txt files
                    file_path = data_dir / filename
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read().strip()  # Read and strip whitespace
                        total_articles += 1

                        # Create a structured document for each text file
                        doc_text = content
                        metadata = {
                            'source': filename  # Use the filename as the source
                        }
                        documents.append(Document(text=doc_text, metadata=metadata))

            # Create index from documents
            parser = SimpleNodeParser.from_defaults()
            nodes = parser.get_nodes_from_documents(documents)
            index = VectorStoreIndex(nodes)

            logging.info(f"Successfully indexed {total_articles} articles")
            return index, total_articles

        except Exception as e:
            logging.error(f"Error loading and indexing files: {str(e)}")
            st.error(f"Error loading and indexing files: {str(e)}")
            return None, 0

    def search_news(self, query: str, index, max_results: int = 5):
        """Search news articles using LlamaIndex."""
        try:
            # Create query engine
            query_engine = index.as_query_engine(
                similarity_top_k=max_results,
                response_mode="no_text"
            )

            # Execute search
            response = query_engine.query(query)

            # Process results
            results = []
            for node in response.source_nodes:
                # Extract article information from node
                article = {
                    'content': node.text,  # Full content of the article
                    'source': node.node.metadata.get('source', 'Unknown Source')  # Metadata for source
                }
                results.append(article)

            logging.info(f"Found {len(results)} relevant articles for query: {query}")
            return results

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

    # Load and index news data
    with st.spinner("Loading and indexing articles..."):
        index, total_articles = NewspaperFinderBot.load_and_index_articles()
        if index:
            st.success(f"Loaded and indexed {total_articles} articles successfully!")
        else:
            st.error("Failed to load articles.")
            return

    # Search interface
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input(
            "Enter your search query:",
            placeholder="Example: Recent political news in Gujarat"
        )
    with col2:
        max_results = st.number_input(
            "Max results",
            min_value=1,
            max_value=20,
            value=5
        )

    # Add filters in the sidebar
    st.sidebar.title("Search Options")
    search_type = st.sidebar.radio(
        "Search Type",
        ["Semantic Search", "Keyword Match"],
        help="Semantic search understands context, keyword match looks for exact terms"
    )

    if st.button("Search", type="primary"):
        if query:
            with st.spinner("Searching..."):
                results = bot.search_news(query, index, max_results)

            if results:
                st.write(f"Found {len(results)} relevant articles:")
                for i, article in enumerate(results, 1):
                    with st.expander(f"{i}. {article.get('source', 'No source')}"):
                        st.write("**Content:**")
                        st.write(article.get('content', 'No content'))
                        st.write(f"**Source:** {article.get('source', 'No source')}")
            else:
                st.warning("No relevant articles found.")
        else:
            st.warning("Please enter a search query.")

    # Add information in the sidebar
    st.sidebar.title("About")
    st.sidebar.info("""
    This app uses AI-powered search to find relevant articles in Gujarati newspapers.

    **Features:**
    - Semantic search
    - Natural language queries
    - Full-text search
    - Article summaries
    """)


if __name__ == "__main__":
    main()
