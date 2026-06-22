from dataclasses import dataclass

from agents import Runner

from app.definitions import build_team_agents
from app.message_bus import TeamBus

MAX_ROUNDS = 6


@dataclass
class MeshResult:
    task: str
    transcript: list
    review: str | None
    rounds: int
    passed: bool


def _print_message(sender: str, recipient: str, content: str) -> None:
    print(f"\n[{sender} → {recipient}]")
    print("-" * 40)
    print(content)


async def run_mesh(task: str) -> MeshResult:
    """Run the full-mesh multi-agent collaboration loop."""
    bus = TeamBus(task)
    bus.post("User", "Team", task)
    _print_message("User", "Team", task)

    agents = build_team_agents(bus)
    rounds_completed = 0

    for round_num in range(1, MAX_ROUNDS + 1):
        print(f"\n{'=' * 60}")
        print(f"  ROUND {round_num}")
        print(f"{'=' * 60}")

        for agent in agents:
            prompt = bus.prompt_for_turn(agent.name, round_num)
            result = await Runner.run(agent, prompt)
            output = result.final_output
            bus.post(agent.name, "Team", output)
            _print_message(agent.name, "Team", output)
            rounds_completed = round_num

        if bus.review_passed():
            break

        if bus.review_failed() and round_num < MAX_ROUNDS:
            notice = "Review failed. Collaborate with your teammates to fix the issues."
            bus.post("System", "Team", notice)
            _print_message("System", "Team", notice)

    review = bus.last_review()
    return MeshResult(
        task=task,
        transcript=bus.transcript,
        review=review,
        rounds=rounds_completed,
        passed=bus.review_passed(),
    )
