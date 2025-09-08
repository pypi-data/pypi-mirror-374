from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from programming_game.structure.instance_character import InstanceCharacter


@dataclass
class Instance:
    instance_id: str
    time: int = 0
    characters: dict[str, "InstanceCharacter"] = field(default_factory=dict)
    playersSeekingParty: dict[str, str] = field(default_factory=dict)
