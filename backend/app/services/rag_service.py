from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging_config import logger
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.llm_service import LLMService


class RAGService:
    def __init__(
        self,
        embedding_service: EmbeddingService = None,
        vector_store: VectorStore = None,
        llm_service: LLMService = None
    ):
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore()
        self.llm_service = llm_service or LLMService()

    def retrieve_context(self, question: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Embed question and perform similarity search against ChromaDB.
        """
        k = top_k or settings.TOP_K
        query_embedding = self.embedding_service.embed_text(question)
        results = self.vector_store.search(query_embedding, top_k=k)
        return results

    def build_prompt(self, question: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Construct structured LLM prompt with retrieved contexts.
        """
        context_blocks = []
        for idx, chunk in enumerate(context_chunks, 1):
            meta = chunk["metadata"]
            doc_name = meta.get("filename", "Unknown Document")
            page_info = f" (Page {meta.get('page')})" if meta.get("page") else ""
            chunk_text = chunk["text"]
            context_blocks.append(f"--- Document Chunk {idx} [{doc_name}{page_info}] ---\n{chunk_text}")

        context_str = "\n\n".join(context_blocks) if context_blocks else "No relevant document context found."

        prompt = f"""Context:
{context_str}

User Question:
{question}

Answer:"""
        return prompt

    def generate_answer(self, question: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Build prompt and generate answer via LLMService.
        """
        if not context_chunks:
            return "I could not find this information in the uploaded documents."

        prompt = self.build_prompt(question, context_chunks)
        return self.llm_service.generate(prompt)

    def answer_question(self, question: str, top_k: int = None) -> Dict[str, Any]:
        """
        End-to-end RAG pipeline execution.
        Returns dict containing 'answer' and list of formatted 'sources'.
        """
        logger.info(f"Executing RAG pipeline for query: '{question}'")
        retrieved_results = self.retrieve_context(question, top_k=top_k)

        sources = []
        for item in retrieved_results:
            meta = item["metadata"]
            preview_text = item["text"][:200] + "..." if len(item["text"]) > 200 else item["text"]
            sources.append({
                "document_id": int(meta.get("document_id", 0)),
                "filename": str(meta.get("filename", "unknown")),
                "page": int(meta.get("page")) if meta.get("page") is not None else None,
                "chunk_index": int(meta.get("chunk_index", 0)),
                "similarity": float(item["similarity"]),
                "preview": preview_text
            })

        answer = self.generate_answer(question, retrieved_results)

        return {
            "answer": answer,
            "sources": sources
        }
