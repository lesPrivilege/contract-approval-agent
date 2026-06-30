"""LLM provider configuration — switchable via environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()


def get_llm():
    """Return a LangChain chat model based on env vars."""
    provider = os.getenv("LLM_PROVIDER", "openai")
    model = os.getenv("LLM_MODEL", "gpt-4.1-mini")

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model)
    else:
        from langchain.chat_models import init_chat_model
        return init_chat_model(model, model_provider=provider)
