import webbrowser
import requests

def open_website(url: str):
    if not url or not url.strip():
        raise ValueError("url must be a non-empty string")

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    webbrowser.open(url)
    return url

def web_search(query: str) -> str:
    if not query or not query.strip():
        raise ValueError("query must be a non-empty string")

    url = f"https://www.google.com/search?q={requests.utils.quote(query)}"

    webbrowser.open(url)
    return url