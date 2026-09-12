from tools.search import open_website, web_search
from tools.alarm import add_alarm, remove_alarm
from tools.notes import save_note, read_note
from tools.email import check_email

def parse_decision(decision: str):
    action, _ , payload = decision.partition("|")
    return (action.strip().upper(),payload.strip())

def split_payload(payload: str, count: int):
    parts = payload.split("|", count - 1)
    if len(parts) != count:
        raise ValueError(f"Expected {count} arguments, got {len(parts)}")

    return [part.strip() for part in parts]

# Tool handlers
def handle_save(payload):
    return save_note(payload)

def handle_search(payload):
    return web_search(payload)

def handle_open(payload):
    return open_website(payload)

def handle_email(payload):
    result = check_email() if payload == "None" else check_email(int(payload))
    return result


# alarm handlers 

def handle_add_alarm(payload):
    alarm_time, description, persist = split_payload(payload, 3)
    return add_alarm(alarm_time, description, bool(persist))

def handle_remove_alarm(payload):
    alarm_id = int(payload)
    return remove_alarm(alarm_id)

TOOL_HANDLERS = {
    "SAVE": handle_save,
    "SEARCH": handle_search,
    "OPEN": handle_open,
    "ADD_ALARM": handle_add_alarm,
    "REMOVE_ALARM": handle_remove_alarm,
    "EMAIL": handle_email,
}