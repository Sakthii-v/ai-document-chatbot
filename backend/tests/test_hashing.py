from app.utils.hashing import compute_file_hash


def test_sha256_hashing_consistency():
    content1 = b"Sample text document content for SHA256 testing."
    content2 = b"Sample text document content for SHA256 testing."
    content3 = b"Different content altogether."

    hash1 = compute_file_hash(content1)
    hash2 = compute_file_hash(content2)
    hash3 = compute_file_hash(content3)

    assert len(hash1) == 64
    assert hash1 == hash2, "Identical content must produce identical SHA-256 hash"
    assert hash1 != hash3, "Different content must produce different SHA-256 hash"
