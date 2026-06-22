from dataclasses import dataclass, field


@dataclass
class AgentMessage:
    sender: str
    recipient: str
    content: str


@dataclass
class TeamBus:
    task: str
    messages: list[AgentMessage] = field(default_factory=list)

    def post(self, sender: str, recipient: str, content: str) -> None:
        self.messages.append(AgentMessage(sender, recipient, content))

    @property
    def transcript(self) -> list[AgentMessage]:
        return list(self.messages)

    def format_transcript(self) -> str:
        lines = [f"Task: {self.task}", "", "Team conversation:"]
        for msg in self.messages:
            lines.append(f"[{msg.sender} → {msg.recipient}]: {msg.content}")
        return "\n".join(lines)

    def prompt_for_turn(self, agent_name: str, round_num: int) -> str:
        return (
            f"{self.format_transcript()}\n\n"
            f"--- Round {round_num} | Your turn: {agent_name} ---\n"
            f"Read the conversation above. Post your update to the team. "
            f"Use talk_to_* tools to communicate directly with other agents when needed."
        )

    def last_review(self) -> str | None:
        for msg in reversed(self.messages):
            if msg.sender == "Reviewer" and msg.recipient == "Team":
                return msg.content
        return None

    def _review_verdict(self) -> str | None:
        review = self.last_review()
        if not review:
            return None
        first_line = review.strip().splitlines()[0].upper()
        if "PASS" in first_line:
            return "PASS"
        if "FAIL" in first_line:
            return "FAIL"
        return None

    def review_passed(self) -> bool:
        return self._review_verdict() == "PASS"

    def review_failed(self) -> bool:
        return self._review_verdict() == "FAIL"
