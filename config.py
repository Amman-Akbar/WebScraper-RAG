import os
import logging
import dotenv
import streamlit as st

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
dotenv.load_dotenv()
LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")  # Pinecone API Key
INDEX_NAME = "testing"  # Pinecone Index Name

# Check for missing API keys
if not (LLAMA_API_KEY and GROQ_API_KEY and PINECONE_API_KEY):
    logging.error("One or more required API keys are missing.")
    st.error("Missing API keys. Please check your environment configuration.")
    st.stop()
