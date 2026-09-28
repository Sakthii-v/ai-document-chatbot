from app.services.chunking_service import ChunkingService


def test_chunking_service_word_split_and_metadata():
    chunker = ChunkingService(chunk_size=10, chunk_overlap=3)
    
    sample_pages = [
        {
            "text": "Word " * 25,  # 25 words
            "page": 1
        }
    ]

    chunks = chunker.chunk_extracted_pages(
        extracted_pages=sample_pages,
        document_id=1,
        filename="test_policy.pdf"
    )

    assert len(chunks) > 1
    assert chunks[0]["id"] == "document_1_chunk_0"
    assert chunks[0]["metadata"]["document_id"] == 1
    assert chunks[0]["metadata"]["filename"] == "test_policy.pdf"
    assert chunks[0]["metadata"]["page"] == 1
    assert chunks[0]["metadata"]["chunk_index"] == 0
