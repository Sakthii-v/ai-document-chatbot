import hashlib


def compute_file_hash(content: bytes) -> str:
    """Compute SHA-256 hash of raw file byte content."""
    sha256 = hashlib.sha256()
    sha256.update(content)
    return sha256.hexdigest()
