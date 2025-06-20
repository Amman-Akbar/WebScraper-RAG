import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from config import GROQ_API_KEY, PINECONE_API_KEY, INDEX_NAME

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

try:
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        encode_kwargs={"normalize_embeddings": True}
    )
    logging.info("Embeddings initialized successfully.")
except Exception as e:
    logging.exception("Error initializing embeddings.")
    raise e

try:
    # Initialize Pinecone client with environment
    pc = Pinecone(api_key=PINECONE_API_KEY, environment="us-east-1")

    # Get existing indexes
    existing_indexes = [index.name for index in pc.list_indexes()]  # Correct extraction

    if INDEX_NAME not in existing_indexes:
        logging.info(f"Creating new Pinecone index: {INDEX_NAME}")
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )

    # Load the index
    index = pc.Index(INDEX_NAME)
    vector_store = PineconeVectorStore(embedding=embeddings, index=index)
    logging.info(f"Connected to Pinecone index: {INDEX_NAME}")

except Exception as e:
    logging.exception("Error initializing Pinecone or vector store.")
    raise e

try:
    # Initialize LLM (ChatGroq)
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    logging.info("ChatGroq LLM initialized successfully.")
except Exception as e:
    logging.exception("Error initializing ChatGroq LLM.")
    raise e

# Set up a prompt template and combine it with the LLM
prompt_template = PromptTemplate(
    input_variables=["question", "context"],
    template=(
        "You are a helpful assistant that answers questions based on the provided context only.\n"
        "The user's question is: {question}\n\n"
        "Context:\n"
        "{context}\n\n"
        "Answer:"
    )
)

# Combine prompt with LLM
sequence = prompt_template | llm

# Expose variables for other modules
__all__ = ["vector_store", "llm", "sequence"]
