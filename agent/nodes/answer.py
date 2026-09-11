from ..agent_state import AgentState
from utils.helpers import parse_decision

def make_answer_node(state: AgentState):
    action, payload = parse_decision(state["decision"])
    
    if action == "ANSWER": return {"response": payload}
    # malformed model output fallback
    return {"response": state["decision"]}