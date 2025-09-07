import msgspec

InventoryType = dict[str, float]


class Trades(msgspec.Struct, forbid_unknown_fields=True):
    """Legacy trade structure - deprecated, use NewTrades instead."""

    wants: dict[str, int] = {}
    offers: dict[str, int] = {}


class NewTrades(msgspec.Struct, forbid_unknown_fields=True):
    """Modern trade structure with prices and quantities."""

    buying: dict[str, dict[str, int]] = {}  # item -> {price: int, quantity: int}
    selling: dict[str, dict[str, int]] = {}  # item -> {price: int, quantity: int}


class UnitTrades(msgspec.Struct):
    """Combined trade structure for units."""

    # wants: dict[str, int] = {}  # deprecated
    # offers: dict[str, float] = {}  # deprecated
    buying: dict[str, dict[str, int]] = {}
    selling: dict[str, dict[str, float]] = {}


class PlayerStats(msgspec.Struct):
    maxHp: int
    maxMp: int
    maxTp: int
    mpRegen: float
    attack: float
    defense: float
    movementSpeed: float
    radius: float


class Position(msgspec.Struct):
    """
    Represents a 2D position with x and y coordinates.

    Provides a straightforward way to store and retrieve 2D positional
    data. Supports creation from a dictionary for flexible initialization.

    :ivar x: The x-coordinate of the position.
    :ivar y: The y-coordinate of the position.
    """

    x: float
    y: float

    def __mul__(self, other: float) -> "Position":
        return Position(self.x * other, self.y * other)

    @classmethod
    def from_dict(cls, other_position: dict[str, float]) -> "Position":
        """
        Creates a Position instance from a dictionary containing x and y values.

        :param other_position: Dictionary with keys "x" and "y" representing position
            coordinates.
        :type other_position: dict
        :return: A new Position instance initialized with the coordinates
            from the input dictionary.
            :rtype: Position
        """
        return Position(other_position["x"], other_position["y"])


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
