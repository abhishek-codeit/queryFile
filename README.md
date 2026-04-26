# QueryFile: High-Performance Local-Cloud Hybrid RAG System

A full-stack Retrieval-Augmented Generation (RAG) application that allows you to chat with your PDF documents. This project combines **local privacy** (for embeddings) with **cloud-scale performance** (for LLM reasoning).

## 🚀 The Architecture

This project is built with a focus on speed and scalability for a personal knowledge base:

- **Orchestration:** [Inngest](https://inngest.com) for reliable, step-based background processing (ingestion & querying).
- **LLM:** [Groq](https://groq.com) (Llama 3.3 70B) for near-instant response generation.
- **Vector Database:** [Qdrant Cloud](https://qdrant.tech) for scalable, high-performance vector search.
- **Local Embedding:** [Ollama](https://ollama.com) (`mxbai-embed-large`) to ensure document processing starts locally.
- **API Framework:** [FastAPI](https://tiangolo.com) for a modern, high-performance backend.

## ✨ Key Features

- **Hybrid Processing:** Uses local Ollama for embeddings to save costs and cloud LLMs for superior reasoning.
- **Event-Driven:** Powered by Inngest to handle long-running PDF ingestion without blocking the API.
- **Efficient Chunking:** Implements LlamaIndex `SentenceSplitter` to maintain context window limits.
- **Scalable Storage:** Managed Qdrant Cloud collection with Cosine Similarity for precise retrieval.

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **AI/ML:** LlamaIndex, Ollama, Groq SDK
- **Database:** Qdrant
- **Backend:** FastAPI, Uvicorn, Inngest

## 📋 Prerequisites

Before running this project, ensure you have:
1. [Ollama](https://ollama.com) installed and running.
2. The embedding model pulled: `ollama pull mxbai-embed-large`.
3. A [Groq API Key](https://groq.com).
4. A [Qdrant Cloud](https://qdrant.io) cluster and API key.

## ⚙️ Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com
   cd queryFile
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file (see `.env.example`):
   ```env
   GROQ_API_KEY=your_key_here
   QDRANT_URL=your_cloud_url
   QDRANT_API_KEY=your_cloud_key
   ```

4. **Run the Application:**
   ```bash
   # Start the Inngest Dev Server
   npx inngest-cli@latest dev

   # Start the FastAPI server
   uvicorn main:app --reload
   ```

## 🛤️ Future Roadmap

- [ ] **Multi-format support:** Integration for Word, Excel, and Markdown files.
- [ ] **Multimedia Library:** Image and Video organization using CLIP embeddings and Whisper transcription.
- [ ] **Automated TTL:** Auto-deletion of temporary files to optimize cloud storage.

---
Developed by [Abhishek](https://github.com/abhishek-codeit)
