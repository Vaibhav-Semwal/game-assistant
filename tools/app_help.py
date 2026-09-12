import subprocess

def open_app(query):
    query = query.strip()
    if not query: return "No application name provided."

    ps = f'''
    $app = Get-StartApps |
        Where-Object {{ $_.Name -like "*{query}*" }} |
        Select-Object -First 1

    if ($app) {{
        Start-Process "shell:AppsFolder\\$($app.AppID)"
    }} else {{
        exit 1
    }}
    '''
    result = subprocess.run(["powershell", "-NoProfile", "-Command", ps],capture_output=True,text=True)
    if result.returncode == 0: return f"Opening {query}"
    return f"Could not find application: {query}"