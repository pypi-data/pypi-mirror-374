from dataclasses import dataclass
from typing import Callable, Coroutine, Any

from programming_game.structure.instance_character import ScriptProtocol

CallableScript = Callable[[], Coroutine[Any, Any, "OnTickResponse"]]


@dataclass
class CallableScriptWrapper(ScriptProtocol):
    """
    Wrapper class for callable-based scripts.

    Allows setup_character to return a simple async function instead of a full script object.
    """

    _callable: CallableScript

    async def on_tick(self) -> "OnTickResponse":
        return await self._callable()
