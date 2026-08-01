import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

DATA_DIR = os.path.join(ROOT_DIR, "data")
DB_DIR = os.path.join(DATA_DIR, "db")
DOCS_DIR = os.path.join(DATA_DIR, "documents")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma")
LOGS_DIR = os.path.join(DATA_DIR, "logs")

for directory in [DATA_DIR, DB_DIR, DOCS_DIR, CHROMA_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

CHROMA_PERSIST_DIR = CHROMA_DIR
OBSERVABILITY_DB_PATH = os.path.join(DB_DIR, "observability.db")
MEMORY_DB_PATH = os.path.join(DB_DIR, "memory.db")

# LLM Provider configuration: "openai", "groq", "gemini", "ollama", or "mock"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
PROMPT_VERSION = "v2"
