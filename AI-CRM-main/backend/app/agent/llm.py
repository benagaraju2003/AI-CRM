"""
Groq LLM client setup via langchain-groq.

Design note: gemma2-9b-it on Groq has inconsistent support for native
OpenAI-style function/tool calling compared to Llama models. Rather than
relying on automatic tool-binding (which can silently fail or hallucinate
args on gemma2), this agent uses a more robust two-stage pattern:
  1. A router node prompts the LLM to output strict JSON naming which tool
     to call and with what arguments.
  2. A tool-execution node parses that JSON and invokes the real Python
     tool function directly.
This keeps tool selection fully under our control and makes the agent's
behavior debuggable and reliable regardless of the underlying model's
native tool-calling support.
"""
from langchain_groq import ChatGroq

from app.config import settings


def get_llm(temperature: float = 0.0) -> ChatGroq:
    """Returns a configured ChatGroq client using the model from settings
    (gemma2-9b-it by default, per assignment spec)."""
    return ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=temperature,
    )
