from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from services.retrieval.embedding import Embedder
from utils.helpers import parse_decision, TOOL_HANDLERS
from .agent_state import AgentState
from services.settings import settings
from .nodes import (
    chunk,
    tool,
    answer,
    planner,
    responder,
    retriever,
)

def route_node(state: AgentState):
    action, _ = parse_decision(state["decision"])
    if action == "ANSWER":return "answer"
    if action == "RAG_MODE": return "rag_mode"
    if action in TOOL_HANDLERS: return "tool"
    # fallback if Qwen generates something unexpected
    return "answer"


# Main Graph
# ------------------------------------------------

embedder = Embedder()

builder = StateGraph(AgentState)

builder.add_node("planner",planner.make_planner_node)
builder.add_node("tool",tool.make_tool_node)
builder.add_node("answer",answer.make_answer_node)
builder.add_node("chunk",chunk.make_chunk_node)
builder.add_node("retriever",retriever.make_retrieve_node)
builder.add_node("responder",responder.make_responder_node)

builder.add_edge(START,"planner")
builder.add_conditional_edges(
    "planner",
    route_node,
    {
        "tool": "tool",
        "answer": "answer",
        "rag_mode": "chunk", 
    }
)
builder.add_edge("chunk", "retriever")
builder.add_edge("retriever", "responder")
builder.add_edge("tool",END)
builder.add_edge("answer",END)
builder.add_edge("responder", END)

graph = builder.compile()