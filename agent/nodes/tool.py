from ..agent_state import AgentState
from utils.helpers import parse_decision, split_payload,TOOL_HANDLERS

def make_tool_node(state: AgentState):
    action, payload = parse_decision(state["decision"])
    handler = TOOL_HANDLERS.get(action)
    if not handler: return {"response": f"Unknown action: {action}"}
    try:
        return {"response": handler(payload)}
    except Exception as e:
        print(f"[TOOL ERROR] {action}: {e}")
        return {"response": f"Failed to execute {action}: {e}"}
