

# Evento de entrada
from datetime import datetime
from traitlets import Any


SUPPORTED_TYPES = {
    "pr_opened",
    "pr_merged",
    "deployment",
    "incident",
}


team_id = "platform"

events = [
    {
        "type": "pr_opened",
        "id": "pr-1",
        "timestamp": "2026-01-01T09:00:00Z"
    },
    {
        "type": "pr_merged",
        "id": "pr-1",
        "timestamp": "2026-01-02T09:00:00Z"
    },
    {
        "type": "deployment",
        "timestamp": "2026-01-03T12:00:00Z"
    },
    {
        "type": "incident",
        "timestamp": "2026-01-04T12:00:00Z"
    }
]

class LLMClient:

    def __init__(self):
        pass

    def send_request(self, prompt: str) -> str:
        # Simula o envio de uma solicitação para um modelo de linguagem
        return f"Simulated response for prompt: {prompt}"
    

    def generate_insight(self, metrics: dict[str, Any]) -> dict[str, Any]:
        # Simula a geração de insight com base nas métricas
        summary = f"The team merged {metrics['merged_prs']} pull request(s) with an average cycle time of {metrics['average_pr_cycle_time_hours']} hours."
        prompt = f"Generate insights based on the following metrics: {summary}"

        try:
            llm_response = self.send_request(prompt)
        except Exception as e:
            llm_response = f"Error generating insight: {str(e)}"

        return {
            "summary": summary,
            "recommendations": llm_response
        }



def calculate_pr_cycle_time(pr_opened_timestamp: str, pr_merged_timestamp: str) -> float:
    opened_time = datetime.fromisoformat(pr_opened_timestamp.replace("Z", "+00:00"))
    merged_time = datetime.fromisoformat(pr_merged_timestamp.replace("Z", "+00:00"))
    cycle_time = (merged_time - opened_time).total_seconds() / 3600.0  # Convert to hours
    return cycle_time

def validate_events(events: list[dict[str, Any]]) -> None:
    if not isinstance(events, list):
        raise ValueError("Events must be a list of dictionaries.")

    if not all(isinstance(event, dict) for event in events):
        raise ValueError("Each event must be a dictionary.")

    if not all(event.get("type") in SUPPORTED_TYPES for event in events):
        raise ValueError(f"All events must have a type in {SUPPORTED_TYPES}.")

    if not all("timestamp" in event for event in events):
        raise ValueError("All events must have a timestamp.")

    if not all(isinstance(event.get("timestamp"), str) for event in events):
        raise ValueError("All event timestamps must be strings.")

def generate_team_insight(
        team_id: str, 
        events: list[dict[str, Any]], 
        llm_client: LLMClient,
        ) -> dict[str, Any]:

    merged_prs = 0
    total_pr_cycle_time = 0.0
    deployments = 0
    incidents = 0

    validate_events(events)

    pr_opened_events = {event["id"]: event for event in events if event["type"] == "pr_opened"}
    pr_merged_events = [event for event in events if event["type"] == "pr_merged"]

    for pr_merged_event in pr_merged_events:
        pr_id = pr_merged_event["id"]
        if pr_id in pr_opened_events:
            pr_opened_timestamp = pr_opened_events[pr_id]["timestamp"]
            pr_merged_timestamp = pr_merged_event["timestamp"]
            cycle_time = calculate_pr_cycle_time(pr_opened_timestamp, pr_merged_timestamp)
            total_pr_cycle_time += cycle_time
            merged_prs += 1

    average_pr_cycle_time_hours = round(total_pr_cycle_time / merged_prs if merged_prs > 0 else 0.0, 2)

    metrics = {
        "merged_prs": merged_prs,
        "average_pr_cycle_time_hours": average_pr_cycle_time_hours,
        "deployments": deployments,
        "incidents": incidents
    }

    for attempt in range(2):
        try:
            llm_response = llm_client.generate_insight(metrics)
            break
        except Exception as e:
            if attempt == 1:
                llm_response = f"Error generating insight: {str(e)}"


    result = {
        "team_id": team_id,
        "metrics": metrics,
        "insight": llm_response
    }

    print(f"Generated insight for team {team_id}: {result}")

    return result

generated_insight = generate_team_insight(team_id, events, LLMClient())
    






