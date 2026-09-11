import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # --- GEMINI & FALLBACK EMBEDDINGS ---
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL")
    FALLBACK_MODEL = os.getenv("FALLBACK_MODEL")
    GEMINI_DIMENSIONS = int(os.getenv("GEMINI_DIMENSIONS"))
    FALLBACK_DIMENSIONS = int(os.getenv("FALLBACK_DIMENSIONS"))

    # --- VECTOR DB (QDRANT) ---
    QDRANT_URL = os.getenv("QDRANT_CLUSTER_ENDPOINT")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION = "enterprise_rag"

    # --- LLM GATEWAY (PORTKEY) ---
    PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY")
    GROQ_SLUG =  "rag"     # primary: @rag/llama-3.3-70b-versatile
    GROQ_SLUG_2 = "brag"  # fallback: @brag/llama-3.1-8b-instant
    
    # --- OBSERVABILITY ---
    LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true")
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "rag_scale_test")
    LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

    # --- CONSTANTS ---
    DEFAULT_COLLECTION = os.getenv("DEFAULT_COLLECTION", "web_rag")
    DEFAULT_SEARCH_RESULTS = int(os.getenv("DEFAULT_SEARCH_RESULTS", "8"))
    DEFAULT_RETRIEVAL_RESULTS = int(os.getenv("DEFAULT_RETRIEVAL_RESULTS", "12"))
    DEFAULT_RERANK_RESULTS = int(os.getenv("DEFAULT_RERANK_RESULTS", "5"))
    DEFAULT_CHUNK_SIZE = int(os.getenv("DEFAULT_CHUNK_SIZE", "1000"))
    DEFAULT_CHUNK_OVERLAP = int(os.getenv("DEFAULT_CHUNK_OVERLAP", "150"))

    WAKE_WORDS = os.getenv("WAKE_WORDS", "jarvis,model").split(",")
    KOKORO_MODEL_PATH = os.getenv("KOKORO_MODEL_PATH", "voices/kokoro-v1.0.onnx")
    KOKORO_VOICES_PATH = os.getenv("KOKORO_VOICES_PATH", "voices/voices-v1.0.bin")
    KOKORO_VOICE = os.getenv("KOKORO_VOICE", "bm_george")
    KOKORO_SPEED = float(os.getenv("KOKORO_SPEED", "1.0"))

    FOLLOWUP_LISTEN_SECONDS = int(os.getenv("FOLLOWUP_LISTEN_SECONDS", "15"))


# Apply LangChain environment variables for automatic tracing
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGSMITH_TRACING", "true")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "rag_scale_test")
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

settings = Settings()