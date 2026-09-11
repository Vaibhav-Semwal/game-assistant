from __future__ import annotations

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from ..settings import settings

# ---------------------------------------------------------------------------
# Qdrant
# ---------------------------------------------------------------------------

def _create_qdrant_client(
    qdrant_url: str | None = None,
    qdrant_api_key: str | None = None,
) -> QdrantClient:
    qdrant_url = qdrant_url or settings.QDRANT_URL
    qdrant_api_key = qdrant_api_key or settings.QDRANT_API_KEY

    if qdrant_url: return QdrantClient(url = qdrant_url, api_key = qdrant_api_key)
    return QdrantClient(":memory:")


def build_vector_store(
    embeddings: Embeddings,
    chunks: list[Document],
    collection_name: str = settings.DEFAULT_COLLECTION,
    qdrant_client: QdrantClient | None = None,
) -> QdrantVectorStore:
    client = qdrant_client or _create_qdrant_client()

    if not client.collection_exists(collection_name):
        sample_vector = embeddings.embed_query("sample text")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=len(sample_vector),
                distance=Distance.COSINE,
            ),
        )

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )

    vector_store.add_documents(documents=chunks)

    return vector_store


def retrieve_documents(
    vector_store: QdrantVectorStore,
    user_input: str,
    k: int = settings.DEFAULT_RETRIEVAL_RESULTS,
) -> list[Document]:
    return vector_store.similarity_search(user_input,k=k)