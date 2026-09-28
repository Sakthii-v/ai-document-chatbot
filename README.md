# AI Document Chatbot Using Python, RAG & Vector Database

A ChatGPT-like web application for intelligent document Question & Answering (QA) powered by Retrieval-Augmented Generation (RAG), Sentence Transformers, persistent ChromaDB vector storage, local Ollama LLM inference, FastAPI, and React.

---

## 🌟 Overview & Key Features

- **Document Processing**: Upload PDF, TXT, and DOCX files with automatic text extraction (preserving PDF 1-indexed page numbers).
- **Smart Chunking & Embeddings**: Splits document pages into overlapping text chunks (500–800 words with 100–150 word overlap) and computes dense vector embeddings using `all-MiniLM-L6-v2`.
- **SHA-256 Duplicate Prevention**: Calculates SHA-256 checksums on upload. Prevents re-extracting, chunking, or embedding duplicate files.
- **Persistent Vector Search**: Stores chunk text, embeddings, and metadata (`document_id`, `filename`, `page`, `chunk_index`) in ChromaDB with cosine similarity search.
- **Strict Local RAG Generation**: Sends top $k=5$ retrieved document chunks as strict context to a local Ollama LLM (`llama3.2:3b` or `qwen2.5:3b`) with prompt guardrails to eliminate hallucination.
- **Source Citations**: Returns exact source citations (file name, page number, chunk index, similarity score, preview snippet) with every assistant response.
- **Conversation History**: Full SQLite persistence for chat threads and messages with multi-session switching and deletion.
- **Modern Responsive UI**: Dark glassmorphic interface inspired by ChatGPT with source cards, auto-scroll, keyboard shortcuts, and real-time Ollama status checking.

---

## 🏗️ Core Architecture

```
                                 +-----------------------+
                                 |     React Frontend    |
                                 +-----------+-----------+
                                             |
                                             | REST API (HTTP)
                                             v
                                 +-----------+-----------+
                                 |    FastAPI Backend    |
                                 +-----+-----------+-----+
                                       |           |
               +-----------------------+           +-----------------------+
               |                                                           |
               v                                                           v
   +-----------+-----------+                                   +-----------+-----------+
   |    Document Service   |                                   |       Chat Service    |
   +-----------+-----------+                                   +-----------+-----------+
               |                                                           |
               v                                                           v
   +-----------+-----------+                                   +-----------+-----------+
   |   Text Extraction     |                                   |        RAG Service    |
   | (PyMuPDF / docx / txt)|                                   +-----------+-----------+
   +-----------+-----------+                                               |
               |                                                           v
               v                                               +-----------+-----------+
   +-----------+-----------+                                   |    Sentence Transformers  |
   |   Chunking Service    |                                   |   (all-MiniLM-L6-v2)  |
   +-----------+-----------+                                   +-----------+-----------+
               |                                                           |
               v                                                           v
   +-----------+-----------+                                   +-----------+-----------+
   |   Embedding Service   |                                   |    ChromaDB VectorStore  |
   +-----------+-----------+                                   |   (Top K Retrieval)   |
               |                                               +-----------+-----------+
               v                                                           |
   +-----------+-----------+                                               v
   | ChromaDB & SQLite DB  |                                   +-----------+-----------+
   +-----------------------+                                   |        Ollama LLM     |
                                                               |   (llama3.2 / qwen)   |
                                                               +-----------+-----------+
                                                                           |
                                                                           v
                                                                    Answer + Sources
```

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, SQLAlchemy (SQLite), Pydantic v2
- **Document Extraction**: PyMuPDF (`fitz`), `python-docx`, Python `open()`
- **Embeddings & Vector Database**: `sentence-transformers` (`all-MiniLM-L6-v2`), ChromaDB (`chromadb`)
- **LLM Engine**: Ollama (Running `llama3.2:3b` or `qwen2.5:3b` locally)
- **Frontend**: React 18, Vite, Lucide Icons, Vanilla CSS Design System

---

## 📂 Project Structure

```
ai-document-chatbot/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/           # Config, logging, exception handlers
│   │   ├── api/            # FastAPI routes (documents, chat, health)
│   │   ├── models/         # SQLAlchemy models (Document, Conversation, Message)
│   │   ├── schemas/        # Pydantic input/output validation schemas
│   │   ├── services/       # Business logic (Extraction, Chunking, Embeddings, RAG, Ollama)
│   │   ├── db/             # Database connection and initialization
│   │   └── utils/          # Hashing (SHA-256) and File Utils
│   ├── tests/              # Pytest unit & integration tests
│   ├── uploads/            # Local document store
│   ├── chroma_data/        # Persistent ChromaDB storage
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/     # Sidebar, ChatWindow, Message, SourceCard, UploadDocument
│   │   ├── pages/          # ChatPage
│   │   ├── services/       # Axios API client
│   │   ├── App.jsx, main.jsx, styles.css
│   ├── package.json
│   └── vite.config.js
│
├── sample_documents/
│   └── company_policy.txt  # Ready-to-use evaluation document
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## 🚀 Quick Setup & Installation

### 1. Ollama Setup

1. Install [Ollama](https://ollama.com/) on your machine.
2. Pull the recommended local LLM model:

```bash
ollama pull llama3.2:3b
```
*(Or alternative model: `ollama pull qwen2.5:3b`)*

3. Start Ollama:
```bash
ollama serve
```

---

### 2. Backend Setup

1. Open terminal and navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a Python virtual environment:

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install required Python packages:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

5. Launch backend dev server:
```bash
uvicorn app.main:app --reload
```
The API documentation (Swagger) will be available at: `http://localhost:8000/docs`

---

### 3. Frontend Setup

1. Open a new terminal tab and navigate to `frontend`:
```bash
cd frontend
```

2. Install dependencies and start Vite dev server:
```bash
npm install
npm run dev
```

3. Open your browser at `http://localhost:5173`

---

## 🧪 Running Automated Tests

Run the test suite using `pytest`:

```bash
cd backend
pytest
```

Tests cover:
- SHA-256 duplicate detection logic
- Document text extraction for TXT & empty file error handling
- Chunking word boundaries & metadata generation
- API `/api/health` service status checks
- End-to-end RAG pipeline response formatting

---

## 📖 RAG Pipeline & Technical Walkthrough

### 1. SHA-256 Duplicate Prevention
When a document is uploaded via `POST /api/documents/upload`, the backend computes its SHA-256 hash. If an identical hash exists in SQLite, processing is skipped, preventing unnecessary vector re-embedding.

### 2. Document Chunking & Page Preservation
For PDFs, page boundaries are preserved so citations pinpoint exact pages (`Page X`). Chunks are generated with 500–800 words and 100–150 word overlaps.

### 3. Vector Search & RAG Context
User questions are converted into embeddings using `all-MiniLM-L6-v2`. ChromaDB returns top $k=5$ matching chunks using cosine similarity. The system prompt enforces strict context adherence:
> *"Answer the user's question using ONLY the provided document context. If the answer cannot be found in the context, clearly say: 'I could not find this information in the uploaded documents.'"*

---

## 📡 Key API Endpoints

- `GET /api/health` — Checks database, ChromaDB, and Ollama status.
- `POST /api/documents/upload` — Upload PDF/DOCX/TXT file.
- `GET /api/documents` — List all uploaded documents.
- `DELETE /api/documents/{id}` — Delete document and its ChromaDB vectors.
- `POST /api/chat` — Submit query, trigger RAG, receive answer + citations.
- `GET /api/conversations` — Fetch chat history.
- `GET /api/conversations/{id}` — Fetch conversation thread messages.
- `DELETE /api/conversations/{id}` — Delete chat thread.

---

## 🐳 Docker Setup (Optional)

Run backend with Docker Compose:

```bash
docker-compose up --build
```

---

## 🛡️ License

MIT License. Built as a technical assignment demonstrator for AI/RAG Engineering.
