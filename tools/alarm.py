import json, threading
from datetime import datetime, date, timedelta
from pathlib import Path
from plyer import notification

DATA_FILE = Path(__file__).parent.parent / "data" / "alarms.json"
stop_event = threading.Event()
_thread = None

def _load():
    return json.load(open(DATA_FILE)) if DATA_FILE.exists() else []

def _save(alarms):
    json.dump(alarms, open(DATA_FILE, "w"), indent=2)
    _list_alarms()

def _cleanup(alarms):
    today = date.today().isoformat()
    kept, changed = [], False
    for a in alarms:
        if a["date"] != today:
            changed = True
            if a["persistent"]:
                a["date"], a["last_fired"] = today, None
                kept.append(a)
            # else: dropped silently, its day is gone
        else:
            kept.append(a)
    return kept, changed

def _list_alarms():
    alarms, changed = _cleanup(_load())
    if changed: _save(alarms)
    if not alarms: print("No alarms set.")
    print("\n".join(f"[{a['id']}] {a['time']} on {a['date']}  {a['label'] or '(no label)'}{ ' [persistent]' if a['persistent'] else '' }" for a in alarms))

def _watch_loop(poll):
    while not stop_event.is_set():
        now, today = datetime.now(), date.today().isoformat()
        alarms, changed = _cleanup(_load())
        remaining = []
        for a in alarms:
            due = a["date"] == today and a["time"] == now.strftime("%H:%M") and a["last_fired"] != today
            if due:
                notification.notify(title="Alarm", message=a["label"] or "Alarm", timeout=15)
                print(f"Fired: {a['label']} ({a['time']})")
                changed = True
                if a["persistent"]:
                    a["last_fired"] = today
                    remaining.append(a)  # one-shot alarms are dropped here
            else:
                remaining.append(a)
        if changed:
            _save(remaining)
        stop_event.wait(poll)




def add_alarm(time_str, label, persistent = False):
    target = datetime.strptime(time_str, "%H:%M").time()  # raises if invalid
    today = date.today()
    armed_date = today if target > datetime.now().time() else today + timedelta(days=1)

    alarms, _ = _cleanup(_load())
    new_id = max([a["id"] for a in alarms], default=0) + 1
    alarms.append({
        "id": new_id, 
        "time": time_str, 
        "label": label,
        "date": armed_date.isoformat(), 
        "persistent": persistent, 
        "last_fired": None
    })
    _save(alarms)
    return f"Added Alarm — {label or '(no label)'}"

def remove_alarm(alarm_id):
    alarms = [a for a in _load() if a["id"] != alarm_id]
    _save(alarms)
    return f"Removed Alarm #{alarm_id}"

def start_watcher(poll=60):

    global _thread
    if _thread and _thread.is_alive():
        return _thread
    stop_event.clear()
    _thread = threading.Thread(target=_watch_loop, args=(poll,), daemon=True)
    _thread.start()
    print(f"Alarm watcher started (every {poll}s).")
    return _thread