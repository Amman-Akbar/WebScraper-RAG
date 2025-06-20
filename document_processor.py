import logging
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from vector_store_setup import vector_store  # Pinecone vector store

def load_and_process_document(md_file: str) -> str:
    """
    Loads the structured Markdown, splits it into chunks, and indexes them in Pinecone.
    Returns a success message or an error message.
    """
    try:
        logging.info(f"Loading document: {md_file}")
        loader = TextLoader(md_file, encoding="utf-8")
        docs = loader.load()  # Load the document
        logging.info(f"Document loaded successfully: {md_file}")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
        chunks = text_splitter.split_documents(docs)  # Split document into chunks
        total_chunks = len(chunks)
        logging.info(f"Document split into {total_chunks} chunks.")

        # Insert chunks into Pinecone
        vector_store.add_documents(chunks)

        logging.info("All chunks inserted successfully into Pinecone.")
        return "Document processed and embeddings stored successfully in Pinecone!"
    except Exception as e:
        error_msg = f"Error processing document {md_file}: {e}"
        logging.error(error_msg)
        return error_msg
