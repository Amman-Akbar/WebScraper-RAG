# 🌍 GlobalApply AI Scraper & RAG System

A powerful Retrieval-Augmented Generation (RAG) application that scrapes web content, processes it into structured data, and enables intelligent question-answering through a conversational interface.

## 🚀 Features

- **Web Scraping**: Automatically extracts text, images, and PDFs from any URL
- **Content Processing**: Converts scraped content into structured markdown using LlamaParse
- **Vector Storage**: Stores processed content in Pinecone vector database for semantic search
- **Intelligent Q&A**: Chat-like interface for asking questions about scraped content
- **Streamlit UI**: User-friendly web interface for easy interaction
- **Automatic Cleanup**: Removes temporary files after processing

## 🏗️ Architecture

```
User Input → Web Scraping → Content Processing → Vector Storage → RAG Q&A
     ↓           ↓              ↓                ↓           ↓
  Streamlit   Selenium    LlamaParse API    Pinecone    Groq LLM
```

## 📋 Prerequisites

- Python 3.8+
- Chrome browser (for Selenium web scraping)
- API keys for:
  - [LlamaParse](https://cloud.llamaindex.ai/) (for PDF processing)
  - [Groq](https://console.groq.com/) (for LLM inference)
  - [Pinecone](https://www.pinecone.io/) (for vector storage)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Amman-Akbar/WebScraper-RAG.git
   cd UPDATED-RAG
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   LLAMA_API_KEY=your_llama_parse_api_key
   GROQ_API_KEY=your_groq_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   ```

## 🚀 Usage

1. **Start the application**
   ```bash
   streamlit run main.py
   ```

2. **Scrape content**
   - Enter a URL in the "Scraping Options" section
   - Choose whether to scrape images and PDFs
   - Click "Scrape & Process"

3. **Ask questions**
   - Use the chat interface to ask questions about the scraped content
   - The system will retrieve relevant information and generate answers

4. **Manage data**
   - Use "Delete Vector DB" to clear stored embeddings
   - Temporary files are automatically cleaned up after processing

## 📁 Project Structure

```
UPDATED RAG/
├── main.py                 # Streamlit application entry point
├── scraper.py             # Web scraping functionality
├── llama_parser.py        # PDF processing with LlamaParse
├── document_processor.py  # Document chunking and vectorization
├── rag.py                 # RAG pipeline implementation
├── vector_store_setup.py  # Pinecone and LLM configuration
├── config.py              # Configuration and API key management
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Technical Details

### Core Components

- **Web Scraping**: Uses Selenium for JavaScript-rendered content and BeautifulSoup for parsing
- **Content Processing**: LlamaParse API converts PDFs to structured markdown
- **Vector Database**: Pinecone serverless index with BAAI/bge-small-en-v1.5 embeddings
- **Language Model**: Groq's llama-3.3-70b-versatile for text generation
- **Text Chunking**: RecursiveCharacterTextSplitter with 500-character chunks and 200-character overlap

### Data Flow

1. **Input**: URL provided by user
2. **Scraping**: Extract text, images, and PDFs from webpage
3. **Consolidation**: Combine all content into a single PDF
4. **Processing**: Convert PDF to structured markdown via LlamaParse
5. **Chunking**: Split markdown into smaller, overlapping pieces
6. **Embedding**: Generate vector embeddings for each chunk
7. **Storage**: Store embeddings in Pinecone vector database
8. **Retrieval**: Find relevant chunks for user queries
9. **Generation**: Generate answers using retrieved context

## 🎯 Use Cases

- **Research**: Scrape and analyze academic papers, reports, or documentation
- **Content Analysis**: Extract insights from websites, blogs, or articles
- **Knowledge Management**: Build searchable knowledge bases from web content
- **Customer Support**: Create Q&A systems from product documentation
- **Education**: Develop interactive learning materials from course content

**Made with ❤️** 