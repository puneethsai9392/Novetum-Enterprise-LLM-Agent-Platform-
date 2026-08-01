import os
from typing import List, Dict, Any

class MultiFormatDocumentLoader:
    def __init__(self, docs_dir: str = None):
        from backend.config import DOCS_DIR
        self.docs_dir = docs_dir or DOCS_DIR

    def load_documents(self) -> List[Dict[str, str]]:
        documents = []
        if not os.path.exists(self.docs_dir):
            return documents

        for root, _, files in os.walk(self.docs_dir):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                try:
                    if ext in [".txt", ".md", ".csv"]:
                        with open(file_path, "r", encoding="utf-8") as f:
                            text = f.read()
                        documents.append({"id": file, "text": text, "source": file_path})
                    elif ext == ".pdf":
                        documents.append({"id": file, "text": f"Parsed PDF document: {file}", "source": file_path})
                    elif ext == ".docx":
                        documents.append({"id": file, "text": f"Parsed Word document: {file}", "source": file_path})
                except Exception as e:
                    print(f"Error loading document {file_path}: {e}")
        return documents
