from __future__ import annotations

from typing import TYPE_CHECKING

from agents import Agent, Runner, function_tool

if TYPE_CHECKING:
    from app.message_bus import TeamBus


class PeerRegistry:
    """Holds agent references for peer-to-peer messaging tools."""

    def __init__(self) -> None:
        self.agents: dict[str, Agent] = {}

    def register(self, name: str, agent: Agent) -> None:
        self.agents[name] = agent


def _make_talk_tool(
    bus: TeamBus,
    self_name: str,
    peer_name: str,
    registry: PeerRegistry,
):
    tool_name = f"talk_to_{peer_name.lower()}"

    @function_tool(name_override=tool_name)
    async def talk_to_peer(message: str) -> str:
        peer = registry.agents[peer_name]
        bus.post(self_name, peer_name, message)
        prompt = (
            f"{bus.format_transcript()}\n\n"
            f"Direct message from {self_name} to {peer_name}:\n{message}\n\n"
            f"Reply as {peer_name}. Be concise and helpful."
        )
        result = await Runner.run(peer, prompt)
        reply = result.final_output
        bus.post(peer_name, self_name, reply)
        return reply

    talk_to_peer.__doc__ = (
        f"Send a direct message to {peer_name} and receive their reply. "
        f"Use this to ask questions or coordinate with {peer_name}."
    )
    return talk_to_peer


def make_talk_tools(
    bus: TeamBus,
    self_name: str,
    peer_names: list[str],
    registry: PeerRegistry,
) -> list:
    return [_make_talk_tool(bus, self_name, peer, registry) for peer in peer_names]
