import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from rag import query_knowledge_base 

def add_calculator(num1:float,num2:float) -> float:
    """
    This function is used to add two numbers.
    Parameters:
        num1: The first number.
        num2: The second number.
    Returns:
        The sum of the two numbers.
    """
    print("Calculating...")
    return num1 + num2
def search_knowledge_base(query: str) -> str:
    """
    Searches technical architecture and troubleshooting documentation.
    """
    print(f"Searching vector store for: '{query}'...")
    return query_knowledge_base(query)

def main():
    TOOL_MAP = {
    "add_calculator": add_calculator,
    "search_knowledge_base": search_knowledge_base,
    }
    load_dotenv()
    client = genai.Client() 
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents = (
            "What is the default RPM limit for Enterprise accounts at the API gateway, "
            "and if a client has 2 enterprise keys, what is their combined total RPM?"
            ),
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a strict data-verification agent. "
                "Rule 1: Always cite the exact source text from the knowledge base. "
                "Rule 2: Format your final response strictly as a JSON object with keys: "
                "'fact', 'calculation', 'final_answer'."
            ),
            tools=[add_calculator, search_knowledge_base],
            temperature=0.0,
        ),
    )

    print("--- RAW MODEL RESPONSE ---")
    print("Text:", response.text)
    print("Function calls:", response.function_calls)
 
      
if __name__ == "__main__":
    main()
