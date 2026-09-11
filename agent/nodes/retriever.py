from services.settings import settings
from ..agent_state import AgentState
from services.retrieval import ranking_service, qdrant_service
from flashrank import Ranker


def make_retrieve_node(
    state: AgentState,
    ranker: Ranker = Ranker(),
    rerank_k: int = settings.DEFAULT_RERANK_RESULTS,
    retrieval_k: int = settings.DEFAULT_RETRIEVAL_RESULTS,
):
    vector_store = state.get("vector_store")
    input = state.get("rag_input","")
    documents = ranking_service.rerank_documents(
        documents=qdrant_service.retrieve_documents(
            vector_store = vector_store,
            user_input = input,
            k=retrieval_k,
        ),
        user_input= input,
        top_n=rerank_k,
        ranker=ranker,
    )
    return {"reranked_documents": documents}