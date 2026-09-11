import subprocess
import email as email_lib
from datetime import datetime
from email.header import decode_header
from datetime import datetime, timedelta

def create_alarm(time_str: str, description: str):
    """
    Creates a persistent one-time Windows alarm using Task Scheduler.
    `time_str` must be 24-hour "HH:MM" format.
    The alarm fires by beeping repeatedly and showing a popup with
    `description`, even if this Python script/app is no longer running.

    The task is visible/editable/deletable by the user in Task Scheduler
    (search "Task Scheduler" in Start menu -> Task Scheduler Library).
    """
    try:
        hh, mm = map(int, time_str.split(":"))
        assert 0 <= hh <= 23 and 0 <= mm <= 59
    except Exception:
        raise ValueError("time_str must be in 24-hour 'HH:MM' format")

    now = datetime.now()
    target = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)  # schedule for tomorrow if time has passed

    task_name = f"PyAlarm_{target.strftime('%Y%m%d_%H%M%S')}"

    # PowerShell payload: beep a few times, then show a popup with the message.
    # Escaping quotes carefully since this gets passed through schtasks -> cmd -> powershell.
    safe_desc = description.replace('"', "'")
    ps_command = (
        f"for ($i=0; $i -lt 5; $i++) {{ [console]::beep(1000,400); Start-Sleep -Milliseconds 200 }}; "
        f"Add-Type -AssemblyName PresentationFramework; "
        f"[System.Windows.MessageBox]::Show('{safe_desc}', 'Alarm')"
    )

    action = f'powershell.exe -WindowStyle Hidden -Command "{ps_command}"'

    result = subprocess.run(
        [
            "schtasks", "/create",
            "/tn", task_name,
            "/tr", action,
            "/sc", "once",
            "/st", target.strftime("%H:%M"),
            "/sd", target.strftime("%m/%d/%Y"),
            "/f",  # overwrite if a task with the same name exists
        ],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to create alarm task: {result.stderr.strip()}")

    return {
        "task_name": task_name,
        "scheduled_for": target.isoformat(),
        "description": description,
        "status": "created"
    }


def cancel_alarm(task_name: str):
    """Deletes a previously created alarm task by its name."""
    result = subprocess.run(
        ["schtasks", "/delete", "/tn", task_name, "/f"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to delete alarm task: {result.stderr.strip()}")
    return {"task_name": task_name, "status": "cancelled"}


def list_alarms():
    """Lists all alarm tasks created by this system (prefix 'PyAlarm_')."""
    result = subprocess.run(
        ["schtasks", "/query", "/fo", "LIST"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to list tasks: {result.stderr.strip()}")

    alarms = []
    current = {}
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("TaskName:"):
            name = line.split(":", 1)[1].strip().lstrip("\\")
            if name.startswith("PyAlarm_"):
                current = {"task_name": name}
                alarms.append(current)
        elif current and line.startswith("Next Run Time:"):
            current["next_run"] = line.split(":", 1)[1].strip()

    return alarms