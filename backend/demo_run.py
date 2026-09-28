import time
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000/api"


def run_demo():
    print("=" * 70)
    print("🚀 RUNNING LIVE WALKTHROUGH DEMO FOR AI DOCUMENT CHATBOT")
    print("=" * 70)

    # 1. Health check
    print("\n1️⃣ HEALTH CHECK (GET /api/health)")
    res = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {res.status_code}")
    print("Response JSON:")
    print(json.dumps(res.json(), indent=2))

    # 2. Upload Document (sample_documents/company_policy.txt)
    print("\n2️⃣ UPLOADING DOCUMENT (POST /api/documents/upload)")
    doc_path = "sample_documents/company_policy.txt"
    with open(doc_path, "rb") as f:

        files = {"file": ("company_policy.txt", f, "text/plain")}
        res = requests.post(f"{BASE_URL}/documents/upload", files=files)
    print(f"Status Code: {res.status_code}")
    print("Response JSON:")
    doc_data = res.json()
    print(json.dumps(doc_data, indent=2))

    # 3. Duplicate Document Detection Check
    print("\n3️⃣ SHA-256 DUPLICATE DETECTION TEST (Re-uploading same file)")
    with open(doc_path, "rb") as f:
        files = {"file": ("company_policy.txt", f, "text/plain")}
        res = requests.post(f"{BASE_URL}/documents/upload", files=files)
    print(f"Status Code: {res.status_code}")
    print("Response JSON:")
    print(json.dumps(res.json(), indent=2))

    # 4. List Documents
    print("\n4️⃣ LIST DOCUMENTS (GET /api/documents)")
    res = requests.get(f"{BASE_URL}/documents")
    print(json.dumps(res.json(), indent=2))

    # 5. Ask Question via RAG
    print("\n5️⃣ SUBMITTING RAG CHAT QUESTION (POST /api/chat)")
    payload = {"message": "What is the annual leave policy?"}
    res = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status Code: {res.status_code}")
    print("Response JSON:")
    chat_resp = res.json()
    print(json.dumps(chat_resp, indent=2))

    # 6. List Conversations
    print("\n6️⃣ LIST CONVERSATION HISTORY (GET /api/conversations)")
    res = requests.get(f"{BASE_URL}/conversations")
    print(json.dumps(res.json(), indent=2))

    print("\n" + "=" * 70)
    print("✅ DEMO WALKTHROUGH COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    time.sleep(1)
    run_demo()
