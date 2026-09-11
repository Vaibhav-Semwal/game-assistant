from ..agent_state import AgentState
from settings import settings
from services.main import fetch_search_results, search_web
from services.retrieval import qdrant_service, embedding

from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.helpers import parse_decision

def make_chunk_node(state: AgentState) :
    action, payload = parse_decision(state["decision"])
    results = search_web(payload, max_results = settings.DEFAULT_SEARCH_RESULTS)
    documents = fetch_search_results(results)
    splitter = RecursiveCharacterTextSplitter(chunk_size = settings.DEFAULT_CHUNK_SIZE, chunk_overlap = settings.DEFAULT_CHUNK_OVERLAP)
    chunks = splitter.split_documents(documents)
    vector_store = qdrant_service.build_vector_store(
        embeddings=embedding.Embedder().embeddings,
        chunks=chunks,
        collection_name=settings.DEFAULT_COLLECTION
    )
    return {"rag_input": payload, "vector_store": vector_store}