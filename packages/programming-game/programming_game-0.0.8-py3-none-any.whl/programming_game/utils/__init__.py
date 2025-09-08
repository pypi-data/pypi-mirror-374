import math
import re
from functools import lru_cache

from ..schema.position import Position


def get_distance(pos1: Position, pos2: Position) -> float:
    """Calculates the Euclidean distance between two points."""
    return math.sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2)


def check_position_is_equal(pos1: dict[str, float], pos2: dict[str, float], tolerance: float = 0.01) -> bool:
    """Checks if two positions are equal within a tolerance."""
    return abs(pos1["x"] - pos2["x"]) <= tolerance and abs(pos1["y"] - pos2["y"]) <= tolerance


@lru_cache(maxsize=512)
def to_snake_case(name: str) -> str:
    """
    Konvertiert einen String von CamelCase, PascalCase, etc., in snake_case.
    Behandelt Akronyme und andere komplexe Fälle.
    """
    # Fügt einen Unterstrich vor Akronyme und Wortanfänge ein.
    # z.B. "HTTPRequest" -> "HTTP_Request"
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)

    # Fügt einen Unterstrich zwischen Kleinbuchstaben/Ziffern und Großbuchstaben ein.
    # z.B. "myVariable" -> "my_Variable"
    name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)

    return name.lower()
