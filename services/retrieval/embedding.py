from settings import settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

class Embedder:
    def __init__(self, api_key: str | None = None):
        try:
            self.backend = "gemini"
            self.dimensions = settings.GEMINI_DIMENSIONS
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=f"models/{settings.GEMINI_MODEL}",
                google_api_key=api_key or settings.GEMINI_API_KEY,
                output_dimensionality=settings.GEMINI_DIMENSIONS,
            )
        except Exception as e:
            print(f"[embeddings] Gemini unavailable ({e}); falling back to {settings.FALLBACK_MODEL}")
 
            self.backend = "fallback"
            self.dimensions = settings.FALLBACK_DIMENSIONS
            self.embeddings = HuggingFaceEmbeddings(model_name=settings.FALLBACK_MODEL)