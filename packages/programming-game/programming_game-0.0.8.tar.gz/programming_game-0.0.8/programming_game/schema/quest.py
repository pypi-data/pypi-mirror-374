import msgspec

from programming_game.schema.position import Position


class GatherQuestStep(msgspec.Struct, tag="gather"):
    """Quest step to gather items."""

    targets: dict[str, int]


class KillQuestStep(msgspec.Struct, tag="kill"):
    """Quest step to kill monsters."""

    targets: dict[str, int]


class ActiveKillQuestStep(msgspec.Struct, tag="kill"):
    """Quest step to kill monsters."""

    targets: dict[str, dict[str, int]]


class GotoQuestStep(msgspec.Struct, tag="goto"):
    """Quest step to go to a position."""

    position: Position


class TurnInQuestStep(msgspec.Struct, tag="turn_in"):
    """Quest step to turn in the quest."""

    target: str
    requiredItems: dict[str, int] = {}
    position: Position | None = None


ActiveQuestStep = GatherQuestStep | ActiveKillQuestStep | GotoQuestStep | TurnInQuestStep
AvailableQuestStep = GatherQuestStep | KillQuestStep | GotoQuestStep | TurnInQuestStep


class QuestRewards(msgspec.Struct):
    """Rewards for completing a quest."""

    items: dict[str, int] = {}


class Quest(msgspec.Struct):
    """Represents a quest with its details and requirements."""

    id: str
    name: str


class AvailableQuest(Quest):
    """A quest available from an NPC."""

    repeatable: bool
    rewards: QuestRewards
    steps: list[AvailableQuestStep]


class ActiveQuest(Quest):
    """An active quest that a player is working on."""

    start_npc: str
    end_npc: str
    steps: list[ActiveQuestStep]
