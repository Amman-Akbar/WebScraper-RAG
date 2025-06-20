import logging
from vector_store_setup import vector_store, sequence

def retrieve_documents(query: str) -> str:
    """
    Retrieves relevant documents from the Pinecone vector store based on the query.
    Returns the combined content of the retrieved documents.
    """
    try:
        results = vector_store.similarity_search(query, k=10)
        if not results:
            logging.info(f"No relevant context found for query: {query}")
            return None  # Return None for better handling in rag_answer()

        return "\n\n".join([result.page_content for result in results])
    except Exception as e:
        error_msg = f"Error retrieving documents: {e}"
        logging.error(error_msg)
        return None  # Ensure None is returned instead of an error message

def rag_answer(query: str) -> str:
    """
    Generates an answer using the RAG pipeline by querying Pinecone.
    Returns the generated answer or an error message.
    """
    try:
        context = retrieve_documents(query)
        if not context:
            return "I'm sorry, but I couldn't find relevant information in the database."

        result = sequence.invoke({"question": query, "context": context})

        # Handle different return types properly
        if hasattr(result, "content"):
            return result.content
        elif isinstance(result, dict) and "content" in result:
            return result["content"]
        elif isinstance(result, str):
            return result
        else:
            logging.warning(f"Unexpected response format: {result}")
            return str(result)
    except Exception as e:
        error_msg = f"Error generating answer: {e}"
        logging.error(error_msg)
        return "An error occurred while generating the answer. Please try again."
