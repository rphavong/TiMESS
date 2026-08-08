# Mem0 - Long-term per user memory usage tracking
## Mem0 is a service that allows you to store and retrieve long-term memory for users of your application. 
## This module provides a simple interface to interact with Mem0, including searching for relevant memories and saving new interactions per user.
import os

from mem0 import MemoryClient

MEM0_API_KEY = os.getenv("MEM0_API_KEY")

_client = None


def get_client():
    global _client
    if _client is None:
        _client = MemoryClient(api_key=MEM0_API_KEY)
    return _client


def get_user_memories(user_id: str, question: str) -> str:
    """
    Searches Mem0 for memories relevant to the current question,
    scoped to this user. Returns "" (not an error) if Mem0 isn't
    configured or the call fails -- memory is a nice-to-have that
    personalizes answers, never a hard dependency that should be
    able to break the chatbot if Mem0 has an outage.
    """
    if not MEM0_API_KEY:
        return ""
    try:
        client = get_client()
        results = client.search(query=question, user_id=user_id, limit=5)
        if not results:
            return ""
        return "\n".join(f"- {r['memory']}" for r in results)
    except Exception:
        return ""


def save_turn_to_memory(user_id: str, question: str, answer: str) -> None:
    """
    Sends the latest exchange to Mem0, which decides on its own what
    (if anything) is worth remembering long-term about this user --
    we don't write that extraction logic ourselves.
    """
    if not MEM0_API_KEY:
        return
    try:
        client = get_client()
        client.add(
            messages=[
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            ],
            user_id=user_id,
        )
    except Exception:
        pass