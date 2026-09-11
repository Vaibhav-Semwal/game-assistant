from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from models.model import get_langchain_llm 
from prompts.system import SYSTEM_PROMPT
from prompts.game_assistant import GAME_ASSISTANT_PROMPT
from tools.screen_help import image_to_base64,capture_screen

from ..agent_state import AgentState

llm = get_langchain_llm()

def make_planner_node(state: AgentState):
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=state["user_input"])
    ])
    decision = response.content.strip()
    return {"decision": decision}