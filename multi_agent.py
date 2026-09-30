import os
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ==========================================
# 1. LOW-LEVEL SPECIALIST TOOLS
# ==========================================

def inspect_and_cancel_stuck_queries(max_duration_seconds: int = 60) -> str:
    """
    Database tool: Inspects active queries in PostgreSQL and cancels any
    queries running longer than max_duration_seconds.
    """
    print(f"\n[DB Tool] Scanning pg_stat_activity for queries > {max_duration_seconds}s...")
    # Simulating finding and cancelling a rogue analytics query
    return (
        f"SUCCESS: Identified 2 rogue queries running for 84s. "
        f"Executed pg_cancel_backend(pid=4812) and pg_cancel_backend(pid=4819). "
        f"Active client connection count dropped from 150/150 to 18/150."
    )


def rollback_canary_deployment(service_name: str, target_revision: str = "stable") -> str:
    """
    DevOps tool: Executes an immediate Argo Rollouts rollback to the stable revision.
    """
    print(f"\n[DevOps Tool] Triggering Argo Rollout rollback for '{service_name}'...")
    return (
        f"SUCCESS: Rollback initiated for '{service_name}'. Traffic shifted 100% back to "
        f"{target_revision} revision. 5xx error rate normalized to 0.02%."
    )


# ==========================================
# 2. WORKER AGENTS (Agent-as-a-Tool)
# ==========================================

def call_database_specialist(task_description: str) -> str:
    """
    Delegates database-related diagnostic or remediation tasks to the
    specialized PostgreSQL DBA agent.
    """
    print(f"\n>>> [Supervisor -> DB Specialist]: '{task_description}'")
    load_dotenv()
    client = genai.Client()
    
    db_agent = client.chats.create(
        model="gemini-3.8-flash",
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are an expert PostgreSQL DBA. You have tools to inspect pools "
                "and terminate stuck transactions. Resolve the issue and return a concise status summary."
            ),
            tools=[inspect_and_cancel_stuck_queries],
            temperature=0.0,
        ),
    )
    response = db_agent.send_message(task_description)
    return response.text


def call_devops_specialist(task_description: str) -> str:
    """
    Delegates deployment, rollback, or cluster management tasks to the
    specialized Site Reliability Engineering (SRE) agent.
    """
    print(f"\n>>> [Supervisor -> DevOps Specialist]: '{task_description}'")
    load_dotenv()
    client = genai.Client()
    
    devops_agent = client.chats.create(
        model="gemini-3.8-flash",
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are an SRE/DevOps engineer. You have tools to manage Argo rollouts "
                "and traffic routing. Execute the deployment task and return a status report."
            ),
            tools=[rollback_canary_deployment],
            temperature=0.0,
        ),
    )
    response = devops_agent.send_message(task_description)
    return response.text


# ==========================================
# 3. SUPERVISOR (ORCHESTRATOR)
# ==========================================

def run_incident_response():
    """
    The Supervisor acts as the Incident Commander. It does not touch raw database
    or cluster tools directly. Instead, it delegates to specialized workers in
    the proper sequence.
    """
    load_dotenv()
    client = genai.Client()

    supervisor = client.chats.create(
        model="gemini-3.8-flash",
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are the Lead Incident Commander. When an incident is reported: "
                "1. First, delegate database remediation to the DB specialist to stabilize connections. "
                "2. Once verified clear, delegate the rollback to the DevOps specialist. "
                "3. Synthesize a unified post-incident summary for the engineering team."
            ),
            tools=[call_database_specialist, call_devops_specialist],
            temperature=0.0,
        ),
    )

    incident_prompt = (
        "INCIDENT ALERT: Canary deployment 'checkout-service' in eu-central-1 is failing. "
        "PgBouncer reports pool exhaustion (150/150). Resolve the database starvation "
        "and roll back the checkout-service canary."
    )

    print("==================================================")
    print("INCIDENT RECEIVED BY SUPERVISOR")
    print("==================================================")
    print(f"Alert: {incident_prompt}\n")

    final_report = supervisor.send_message(incident_prompt)

    print("\n==================================================")
    print("INCIDENT COMMANDER FINAL RESOLUTION REPORT")
    print("==================================================")
    print(final_report.text)


if __name__ == "__main__":
    run_incident_response()
