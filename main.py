import os
import logging
import time
import shutil
import streamlit as st
import pandas as pd
from scraper import scrape_page, combine_text_images_pdfs
from llama_parser import process_pdf_with_llamaparser
from document_processor import load_and_process_document
from rag import rag_answer
from vector_store_setup import vector_store  # Access Pinecone vector store

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

st.title("🌍GlobalApply AI Scraper⛏️📃")

def delete_vector_db():
    """
    Deletes all vectors from the Pinecone index.
    If the namespace is not found (i.e., already cleared), it handles the error gracefully.
    """
    try:
        # Specify the default namespace explicitly (if using default, use "")
        vector_store.delete(delete_all=True, namespace="")
        st.success("Vector database cleared successfully!")
        logging.info("Vector database successfully cleared.")
    except Exception as e:
        error_str = str(e)
        if "Namespace not found" in error_str:
            st.warning("Vector database is already cleared (namespace not found).")
            logging.info("Vector database already cleared (namespace not found).")
        else:
            logging.error(f"Error clearing vector database: {e}")
            st.error(f"Error clearing vector database: {e}")


def main():
    # Section 1: URL Input and Scraping inside an expander (dropdown menu)
    with st.expander("Scraping Options", expanded=False):
        urls = []
        # uploaded_file = st.file_uploader("Upload a CSV file containing URLs", type=["csv"])
        user_url = st.text_input("Or enter a single URL:")

        # Toggle options for scraping images and PDFs
        scrape_images_toggle = st.checkbox("Scrape Images", value=True)
        scrape_pdfs_toggle = st.checkbox("Scrape PDFs", value=True)

        # if uploaded_file:
        #     try:
        #         df = pd.read_csv(uploaded_file)
        #         urls = df.iloc[:, 0].dropna().tolist()
        #     except Exception as e:
        #         st.error(f"Error reading CSV file: {e}")
        #         logging.error(f"Error reading CSV file: {e}")
        # elif user_url:
        #     urls = [user_url]


        # just for testing
        urls=[user_url] 
        # just for testing

        if urls and st.button("Scrape & Process"):
            for url in urls:
                st.write(f"Processing URL: {url}")
                dir_name = scrape_page(url, scrape_images_toggle, scrape_pdfs_toggle)
                if dir_name:
                    # If both toggles are off, simply use the raw text
                    if not (scrape_images_toggle or scrape_pdfs_toggle):
                        txt_file = os.path.join(dir_name, "page_content.txt")
                        md_file = os.path.join(dir_name, "structured_data.md")
                        try:
                            with open(txt_file, "r", encoding="utf-8") as f_in, open(md_file, "w", encoding="utf-8") as f_out:
                                f_out.write(f_in.read())
                            st.success(f"Structured data saved to: {md_file}")
                            logging.info(f"Structured data saved to: {md_file}")
                            message = load_and_process_document(md_file)
                            st.success(message)
                            logging.info(message)
                            if "successfully" in message:
                                try:
                                    shutil.rmtree(dir_name)
                                    logging.info(f"Successfully deleted directory: {dir_name}")
                                    st.info(f"Cleaned up temporary data directory: {dir_name}")
                                except Exception as e:
                                    logging.warning(f"Could not delete directory {dir_name}: {e}")
                                    st.warning(f"Failed to clean up temporary data directory {dir_name}: {e}")
                        except Exception as e:
                            st.error(f"Error creating structured data from text: {e}")
                    else:
                        final_pdf = os.path.join(dir_name, "combined_output.pdf")
                        combined_pdf = combine_text_images_pdfs(dir_name, final_pdf)
                        st.write(f"Combined PDF created: {combined_pdf}")
                        logging.info(f"Combined PDF created: {combined_pdf}")
                        md_file = process_pdf_with_llamaparser(combined_pdf)
                        if md_file:
                            st.success(f"Structured data saved to: {md_file}")
                            message = load_and_process_document(md_file)
                            st.success(message)
                            logging.info(message)
                            if "successfully" in message:
                                try:
                                    shutil.rmtree(dir_name)
                                    logging.info(f"Successfully deleted directory: {dir_name}")
                                    st.info(f"Cleaned up temporary data directory: {dir_name}")
                                except Exception as e:
                                    logging.warning(f"Could not delete directory {dir_name}: {e}")
                                    st.warning(f"Failed to clean up temporary data directory {dir_name}: {e}")
                        else:
                            st.error("Failed to process PDF with LlamaParser.")
                else:
                    st.error(f"Failed to scrape {url}")

    # Section 2: Conversation-like Q&A (mimicking ChatGPT)
    # Initialize session state for conversation and query if not already set.
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "query_input" not in st.session_state:
        st.session_state["query_input"] = ""

    def process_query():
        """Callback function to process the question and update conversation."""
        query = st.session_state["query_input"]
        if query:
            with st.spinner("Generating answer..."):
                answer = rag_answer(query)
            # Prepend the new Q&A so that the latest entry appears at the top.
            st.session_state.conversation = [{"question": query, "answer": answer}] + st.session_state.conversation
            st.session_state["query_input"] = ""  # Clear input field

    # The text input automatically triggers the callback on submission.
    st.text_input(
        "Ask a question about the scraped content:",
        key="query_input",
        on_change=process_query
    )

    # Move the Delete Vector DB button to the top.
    if st.button("Delete Vector DB"):
        delete_vector_db()

    # Display the conversation with the latest question at the top.
    if st.session_state.conversation:
        st.markdown("### Conversation")
        for chat in st.session_state.conversation:
            st.markdown(f"**Question:** {chat['question']}")
            st.markdown(f"**Answer:** {chat['answer']}")
            st.markdown("---")

if __name__ == "__main__":
    main()