import os
import sys

# Ensure backend folder is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.db.init_db import init_db
from app.services.document_service import DocumentService
from app.services.chat_service import ChatService
from app.core.logging_config import setup_logging


class MockUploadFile:
    def __init__(self, file_path: str):
        self.filename = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            self.content = f.read()
        self.file = self

    def read(self):
        return self.content


def main():
    setup_logging()
    init_db()
    db = SessionLocal()

    doc_service = DocumentService(db)
    chat_service = ChatService(db)

    active_conv_id = None

    print("\n" + "=" * 60)
    print(" 🤖 AI DOCUMENT CHATBOT - TERMINAL INTERACTIVE CLI")
    print("=" * 60)

    while True:
        print("\nOPTIONS:")
        print(" [1] Upload a document to RAG Vector Store")
        print(" [2] Ask a question (RAG + Ollama LLM)")
        print(" [3] List all indexed documents")
        print(" [4] View conversation history")
        print(" [5] Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()

        if choice == "1":
            file_path = input("\nEnter document file path (e.g., ../sample_documents/company_policy.txt): ").strip()
            # Clean up quotes if dragged into terminal
            file_path = file_path.strip('"').strip("'")
            if not os.path.exists(file_path):
                print(f"❌ Error: File '{file_path}' not found!")
                continue

            print(f"⏳ Processing and embedding '{os.path.basename(file_path)}'...")
            mock_file = MockUploadFile(file_path)
            try:
                result = doc_service.process_and_save_document(mock_file)
                if result.get("is_duplicate"):
                    print(f"⚠️ DUPLICATE DETECTED: Document already exists in DB! (ID={result['id']}, Chunks={result['chunk_count']})")
                else:
                    print(f"✅ SUCCESS: Processed '{result['filename']}' into {result['chunk_count']} chunks.")
            except Exception as e:
                print(f"❌ Upload Error: {e}")

        elif choice == "2":
            question = input("\nType your question: ").strip()
            if not question:
                print("❌ Question cannot be empty.")
                continue

            print("⏳ Querying ChromaDB vectors and generating LLM answer via Ollama...")
            try:
                result = chat_service.process_chat_message(question=question, conversation_id=active_conv_id)
                active_conv_id = result["conversation_id"]

                print("\n" + "─" * 60)
                print("🤖 ANSWER:")
                print(result["message"])
                print("─" * 60)
                print("📚 RETRIEVED SOURCES:")
                if not result["sources"]:
                    print("  No sources retrieved.")
                else:
                    for idx, src in enumerate(result["sources"], 1):
                        page_str = f" (Page {src['page']})" if src.get("page") else ""
                        sim_pct = round(src['similarity'] * 100, 1)
                        print(f"  [{idx}] 📄 {src['filename']}{page_str} | Chunk {src['chunk_index']} | Match: {sim_pct}%")
                        print(f"      Preview: \"{src['preview'][:120]}...\"")
                print("─" * 60)

            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "3":
            docs = doc_service.list_documents()
            print(f"\n📂 INDEXED DOCUMENTS ({len(docs)} total):")
            if not docs:
                print("  No documents indexed yet.")
            for d in docs:
                print(f"  • [ID {d.id}] {d.filename} ({d.file_type.upper()}, {d.chunk_count} chunks, status: {d.status})")

        elif choice == "4":
            convs = chat_service.list_conversations()
            print(f"\n💬 CONVERSATION SESSIONS ({len(convs)} total):")
            if not convs:
                print("  No conversations recorded yet.")
            for c in convs:
                print(f"  • [ID {c['id']}] {c['title']} ({c['message_count']} messages)")

        elif choice == "5":
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice, please select 1-5.")


if __name__ == "__main__":
    main()
