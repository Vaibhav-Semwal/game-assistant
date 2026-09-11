from langchain_openai import ChatOpenAI

def get_langchain_llm():
    return ChatOpenAI(
        model="Qwen2-VL-3B-Instruct",
        base_url="http://localhost:8080/v1",
        api_key="EMPTY",
        temperature=0.2,
        max_tokens=300,
    )