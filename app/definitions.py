from agents import Agent

from app.mesh_tools import PeerRegistry, make_talk_tools
from app.message_bus import TeamBus
from app.tools import read_file, write_file

PLANNER_INSTRUCTIONS = (
    "You are the Planner on a software development team.\n"
    "- Share a concise markdown plan on the team bus each round you act\n"
    "- Include: approach, steps, files to create (e.g. hello.py, not output/hello.py), "
    "signatures, and edge cases\n"
    "- Use talk_to_coder and talk_to_reviewer to clarify requirements or answer questions\n"
    "- Do not write implementation code\n"
    "- Coordinate with teammates until the task is fully planned"
)

CODER_INSTRUCTIONS = (
    "You are the Coder on a software development team.\n"
    "- Implement the plan using write_file and read_file\n"
    "- Save files by name only (e.g. hello.py) — they are stored in output/ automatically\n"
    "- Use talk_to_planner to clarify the plan or requirements\n"
    "- Use talk_to_reviewer to discuss issues before finalizing\n"
    "- Post a summary on the team bus of what you created or changed each round"
)

REVIEWER_INSTRUCTIONS = (
    "You are the Reviewer on a software development team.\n"
    "- Review code for correctness, edge cases, style, and plan alignment\n"
    "- Use talk_to_coder to request specific fixes\n"
    "- Use talk_to_planner to verify intent when unclear\n"
    "- Post your review to the team bus each round\n"
    "- Start your team-bus review with **PASS** or **FAIL** on the first line, "
    "then provide specific feedback"
)


def build_team_agents(bus: TeamBus) -> list[Agent]:
    """Build Planner, Coder, and Reviewer with full-mesh communication tools."""
    registry = PeerRegistry()

    planner = Agent(
        name="Planner",
        instructions=PLANNER_INSTRUCTIONS,
        tools=make_talk_tools(bus, "Planner", ["Coder", "Reviewer"], registry),
    )
    coder = Agent(
        name="Coder",
        instructions=CODER_INSTRUCTIONS,
        tools=[
            *make_talk_tools(bus, "Coder", ["Planner", "Reviewer"], registry),
            write_file,
            read_file,
        ],
    )
    reviewer = Agent(
        name="Reviewer",
        instructions=REVIEWER_INSTRUCTIONS,
        tools=make_talk_tools(bus, "Reviewer", ["Planner", "Coder"], registry),
    )

    for agent in (planner, coder, reviewer):
        registry.register(agent.name, agent)

    return [planner, coder, reviewer]
