from __future__ import annotations

from flashrank import Ranker, RerankRequest
from langchain_core.documents import Document
from settings import settings

def rerank_documents(
    user_input: str,
    documents: list[Document],
    top_n: int = settings.DEFAULT_RERANK_RESULTS,
    ranker: Ranker | None = Ranker(),
) -> list[Document]:

    if not documents: return []
    
    passages = []
    for index, document in enumerate(documents):
        passages.append({
            "id": index,
            "text": document.page_content,
            "meta": document.metadata,
        })

    request = RerankRequest(query=user_input,passages=passages)
    ranked = ranker.rerank(request)
    reranked_documents: list[Document] = []

    for item in ranked[:top_n]:
        document = documents[item["id"]]
        # Preserve FlashRank score for debugging/observability.
        document.metadata["rerank_score"] = item.get("score")
        reranked_documents.append(document)

    return reranked_documents