from app.services.rag_service import RAGService


class DummyLLMService:
    def generate(self, prompt: str) -> str:
        return "The company provides 18 days of annual leave."


class DummyVectorStore:
    def search(self, query_embedding, top_k=5):
        return [
            {
                "text": "Employees are entitled to 18 days of paid annual leave per calendar year.",
                "metadata": {
                    "document_id": 1,
                    "filename": "employee_policy.pdf",
                    "page": 4,
                    "chunk_index": 2
                },
                "similarity": 0.88
            }
        ]


class DummyEmbeddingService:
    def embed_text(self, text: str):
        return [0.1] * 384


def test_rag_pipeline_output_structure():
    rag = RAGService(
        embedding_service=DummyEmbeddingService(),
        vector_store=DummyVectorStore(),
        llm_service=DummyLLMService()
    )

    result = rag.answer_question("What is the leave policy?")

    assert "answer" in result
    assert "sources" in result
    assert len(result["sources"]) == 1
    source = result["sources"][0]
    assert source["document_id"] == 1
    assert source["filename"] == "employee_policy.pdf"
    assert source["page"] == 4
    assert source["similarity"] == 0.88
    assert "Employees are entitled" in source["preview"]
