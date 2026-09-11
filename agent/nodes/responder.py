from ..agent_state import AgentState
from models.model import get_langchain_llm 
from prompts.game_assistant import GAME_ASSISTANT_PROMPT
from tools.screen_help import image_to_base64,capture_screen
from langchain_core.messages import SystemMessage, HumanMessage

from ..agent_state import AgentState

llm = get_langchain_llm()

def make_responder_node(state: AgentState):    
    input = state.get("rag_input","")
    documents = state.get("reranked_documents", [])

    context_parts = []

    for index, document in enumerate(documents, start=1):
        title = document.metadata.get("title", "Unknown source")
        url = document.metadata.get("url", "Unknown URL")
        context_parts.append(f"""
                SOURCE {index}
                Title: {title}
                URL: {url}

                {document.page_content}
        """.strip())

    context = "\n\n---\n\n".join(context_parts)
    encoded_image = image_to_base64(capture_screen())
    messages = [
        SystemMessage(content=GAME_ASSISTANT_PROMPT.format(context = context)),
        HumanMessage(content=[
                {
                    "type": "text",
                    "text": input,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": (
                            f"data:image/jpeg;base64,"
                            f"{encoded_image}"
                        )
                    },
                },
            ]
        ),
    ]
    response = llm.invoke(messages)
    return {"response": response.content}