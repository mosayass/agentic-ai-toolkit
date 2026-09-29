import time
from dotenv import load_dotenv
from google import genai
from google.genai import types


def safe_divide(num1: float, num2: float) -> str:
    """
    Safely divides num1 by num2.
    If division by zero occurs, returns a descriptive error message
    rather than crashing the application.
    """
    print(f"[Tool Execution] Attempting safe_divide({num1}, {num2})...")
    try:
        if num2 == 0:
            raise ZeroDivisionError("Denominator cannot be zero.")
        result = num1 / num2
        return f"Result: {result}"
    except ZeroDivisionError as e:
        # Instead of crashing, return actionable feedback for the model
        return (
            f"TOOL_ERROR: {str(e)} Please inform the user that division by zero "
            "is mathematically undefined or request a non-zero denominator."
        )


def flaky_network_api(query: str, max_retries: int = 2) -> str:
    """
    Demonstrates Tier 1 Infrastructure Error Handling:
    Retries transient failures locally before escalating to the LLM.
    """
    print(f"[Tool Execution] Querying external API for '{query}'...")
    
    for attempt in range(1, max_retries + 1):
        try:
            # Simulating a transient network hiccup on attempt 1, success on attempt 2
            if attempt == 1:
                print(f"  -> Attempt {attempt} failed: 503 Service Unavailable. Retrying...")
                time.sleep(0.5)
                continue
            
            print(f"  -> Attempt {attempt} succeeded!")
            return f"External Data for '{query}': Service is operational."
        except Exception as e:
            if attempt == max_retries:
                return f"TOOL_ERROR: External API unreachable after {max_retries} retries: {str(e)}"
    
    return "TOOL_ERROR: Max retries exceeded without a response."


def run_error_handling_demo():
    """
    Demonstrates how the agent receives tool error observations
    and translates them into helpful user-facing explanations.
    """
    load_dotenv()
    client = genai.Client()

    chat = client.chats.create(
        model="gemini-3.8-flash",
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a resilient assistant. If a tool returns a TOOL_ERROR, "
                "do not crash. Politely explain the root cause to the user and "
                "suggest how they can fix their input."
            ),
            tools=[safe_divide, flaky_network_api],
            temperature=0.0,
        ),
    )

    print("=== SCENARIO 1: Logical Error (Division by Zero) ===")
    prompt_1 = "Can you calculate 250 divided by 0?"
    print(f"User: {prompt_1}")
    resp_1 = chat.send_message(prompt_1)
    print(f"Agent: {resp_1.text}\n")

    print("=== SCENARIO 2: Transient Infrastructure Error with Auto-Retry ===")
    prompt_2 = "Check the health of our external payment gateway."
    print(f"User: {prompt_2}")
    resp_2 = chat.send_message(prompt_2)
    print(f"Agent: {resp_2.text}\n")


if __name__ == "__main__":
    run_error_handling_demo()
