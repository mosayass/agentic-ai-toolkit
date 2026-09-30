import json
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ==========================================
# 1. LEVEL 1: DETERMINISTIC TOOL CALL EVAL (CI/CD)
# ==========================================

def evaluate_tool_trajectory(actual_call_name: str, actual_args: dict, expected_name: str, expected_keys: list) -> bool:
    """
    Level 1 Eval: Fast, free, deterministic testing (e.g. for pytest).
    Verifies that the agent selected the expected tool and provided the required schema keys.
    """
    if actual_call_name != expected_name:
        print(f"[FAIL] Expected tool '{expected_name}', but agent called '{actual_call_name}'")
        return False
    
    for key in expected_keys:
        if key not in actual_args:
            print(f"[FAIL] Missing required argument '{key}' in tool call.")
            return False
            
    print(f"[PASS] Tool selection '{actual_call_name}' and arguments matched schema.")
    return True


# ==========================================
# 2. LEVEL 2: GROUNDEDNESS & FAITHFULNESS (RAG TRIAD)
# ==========================================

def evaluate_groundedness_heuristic(response_text: str, context_chunk: str) -> float:
    """
    Level 2 Eval: Checks if key factual tokens in the response are grounded
    in the retrieved source text rather than hallucinated from parametric memory.
    """
    # Simple lexical ground check (frameworks like Ragas use decomposed NLI claims)
    keywords = [word.lower() for word in response_text.replace(".", "").replace(",", "").split() if len(word) > 4]
    if not keywords:
        return 1.0
        
    context_lower = context_chunk.lower()
    grounded_count = sum(1 for kw in keywords if kw in context_lower)
    score = grounded_count / len(keywords)
    print(f"[EVAL - Level 2 Groundedness Score]: {score:.2f} (Supported words: {grounded_count}/{len(keywords)})")
    return score


# ==========================================
# 3. LEVEL 3: LLM-AS-A-JUDGE (RUBRIC SCORING)
# ==========================================

JUDGE_PROMPT_TEMPLATE = """
You are an expert AI quality evaluator. Grade the following agent response on a scale of 1 to 5.

EVALUATION RUBRIC:
- 5: Excellent. Factual, strictly supported by the context, and answers the user.
- 3: Acceptable. Partially answers, but lacks detail or includes minor unverified statements.
- 1: Poor / Hallucination. Contradicts the context or fails to answer the question.

CONTEXT:
{context}

USER QUESTION:
{question}

AGENT RESPONSE:
{response}

Output strictly valid JSON with the following structure:
{{
    "score": <integer 1 to 5>,
    "reasoning": "<one sentence explanation>"
}}
"""

def llm_judge_evaluation(client: genai.Client, question: str, context: str, response: str) -> dict:
    """
    Level 3 Eval: Uses a model to grade qualitative adherence against a structured rubric.
    """
    prompt = JUDGE_PROMPT_TEMPLATE.format(
        context=context,
        question=question,
        response=response
    )
    
    eval_result = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json"
        )
    )
    
    return json.loads(eval_result.text)


# ==========================================
# 4. RUNNING THE EVAL SUITE
# ==========================================

def run_eval_suite():
    load_dotenv()
    client = genai.Client()

    print("==================================================")
    print("RUNNING AGENT EVALUATION SUITE")
    print("==================================================")

    # Test Case 1: Level 1 Trajectory Test
    print("\n--- TEST 1: Tool Trajectory Accuracy ---")
    mock_agent_call = {"name": "search_knowledge_base", "args": {"query": "PostgreSQL failover"}}
    evaluate_tool_trajectory(
        actual_call_name=mock_agent_call["name"],
        actual_args=mock_agent_call["args"],
        expected_name="search_knowledge_base",
        expected_keys=["query"]
    )

    # Test Case 2: Level 2 Groundedness Check
    print("\n--- TEST 2: RAG Groundedness Metric ---")
    context = "Patroni orchestrates PostgreSQL failover using Consul consensus if primary is down for 15 seconds."
    good_response = "Patroni initiates failover after 15 seconds using Consul."
    evaluate_groundedness_heuristic(good_response, context)

    # Test Case 3: Level 3 LLM-as-a-Judge
    print("\n--- TEST 3: LLM-as-a-Judge Scoring ---")
    try:
        judge_output = llm_judge_evaluation(
            client=client,
            question="What tool manages PostgreSQL failover?",
            context=context,
            response=good_response
        )
        print(f"Judge Score: {judge_output.get('score')}/5")
        print(f"Judge Reasoning: {judge_output.get('reasoning')}")
    except Exception as e:
        print(f"(API Quota check on Judge execution: {e})")


if __name__ == "__main__":
    run_eval_suite()
