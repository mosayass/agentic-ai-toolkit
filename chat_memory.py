import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from rag import query_knowledge_base


def add_calculator(num1: float, num2: float) -> float:
    """
    Adds two numbers together.
    """
    print(f"Executing add_calculator({num1}, {num2})...")
    return num1 + num2


def search_knowledge_base(query: str) -> str:
    """
    Searches technical architecture and troubleshooting documentation.
    """
    print(f"Executing search_knowledge_base('{query}')...")
    return query_knowledge_base(query)


def run_stateful_chat():
    """
    Demonstrates multi-turn memory using Gemini's native stateful Chat session.
    The session retains previous turns, enabling pronoun resolution (e.g. 'those keys').
    """
    load_dotenv()
    client = genai.Client()

    # Create a stateful chat session with tools and system instruction
    chat = client.chats.create(
        model="gemini-3.8-flash",
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are an enterprise cloud infrastructure assistant. "
                "Answer technical questions accurately using the knowledge base."
            ),
            tools=[add_calculator, search_knowledge_base],
            temperature=0.0,
        ),
    )

    print("=== TURN 1: Initial Question ===")
    user_prompt_1 = "What is the default RPM limit for Enterprise accounts at the API gateway?"
    print(f"User: {user_prompt_1}")
    resp1 = chat.send_message(user_prompt_1)
    print(f"Agent: {resp1.text}\n")

    print("=== TURN 2: Follow-up Question (Relies on Turn 1 Context) ===")
    user_prompt_2 = "If a customer has 2 of those keys, what is their combined total RPM?"
    print(f"User: {user_prompt_2}")
    resp2 = chat.send_message(user_prompt_2)
    print(f"Agent: {resp2.text}\n")

    print("=== INSPECTING INTERNAL CONVERSATION HISTORY ===")
    for idx, message in enumerate(chat.get_history()):
        role = message.role.upper()
        # Parts can contain either text or function_call/function_response
        parts_summary = []
        for part in message.parts:
            if part.text:
                parts_summary.append(f"Text: '{part.text[:60]}...'")
            elif part.function_call:
                parts_summary.append(f"FunctionCall({part.function_call.name})")
            elif part.function_response:
                parts_summary.append(f"FunctionResponse({part.function_response.name})")
        print(f"Message #{idx + 1} [{role}]: {', '.join(parts_summary)}")


def sliding_window_prune(history: list, max_turns: int = 6) -> list:
    """
    Demonstrates a FIFO (First-In, First-Out) sliding window memory buffer.
    In long conversations, keeping only the last N turns prevents context window
    exhaustion and reduces token costs.
    """
    if len(history) > max_turns:
        print(f"[Memory Manager] Pruning history from {len(history)} to {max_turns} messages.")
        return history[-max_turns:]
    return history


if __name__ == "__main__":
    run_stateful_chat()
