import requests
from bs4 import BeautifulSoup

from settings import settings
from duckduckgo_search import DDGS
from langchain_core.documents import Document

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
def search_web(user_input: str,max_results: int = settings.DEFAULT_SEARCH_RESULTS) -> list[dict[str, str]]:
    """
    Search the web using DuckDuckGo.

    Returns:[{
        "title": "...",
        "url": "...",
        "snippet": "..."
    }]
    """
    results: list[dict[str, str]] = []
    with DDGS() as ddgs:
        for result in ddgs.text(user_input,max_results=max_results):
            url = result.get("href") or result.get("url")
            if not url: continue
            results.append({
                "title": result.get("title", ""),
                "url": url,
                "snippet": result.get("body", ""),
            })

    return results

# ---------------------------------------------------------------------------
# Web page extraction
# ---------------------------------------------------------------------------

def _fetch_webpage(url: str, timeout: int = 15) -> str:
    """
    Download a webpage and extract readable text.
    """
    response = requests.get(url,headers={"User-Agent": settings.USER_AGENT},timeout=timeout)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove content that is usually not useful for RAG.
    for tag in soup(["script", "style", "noscript", "svg", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def fetch_search_results(search_results: list[dict[str, str]]) -> list[Document]:
    """
    Fetch all discovered webpages and convert them to LangChain Documents.
    """
    documents: list[Document] = []
    for result in search_results:
        try:
            content = _fetch_webpage(result["url"])
            if not content: continue
            documents.append(Document(
                page_content=content,
                metadata={
                    "title": result["title"],
                    "url": result["url"],
                    "snippet": result["snippet"],
                },
            ))

        except Exception as exc:
            # A single broken website should not kill the entire RAG run.
            print(f"[web-rag] Failed to fetch {result['url']}: {exc}")

    return documents