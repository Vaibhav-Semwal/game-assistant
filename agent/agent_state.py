from typing import TypedDict, List, Optional, Any
from langchain_core.documents import Document

class AgentState(TypedDict):
    decision: str
    response: str                

    user_input: str
    rag_input: str
    vector_store: Any
    reranked_documents: list[Document]
    