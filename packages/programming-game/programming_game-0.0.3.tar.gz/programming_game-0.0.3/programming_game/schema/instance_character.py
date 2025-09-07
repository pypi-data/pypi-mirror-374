import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, Union

from ..logging import logger
from . import events
from .other import Position
from .units import AnyUnit, Monster

if TYPE_CHECKING:
    from .. import GameState
    from ..intents import AnyIntent
    from .game_object import AnyGameObject


# OnTick Response Types for on_tick method
# - AnyIntent: Send intent to server
# - int/float: Pause next tick by this many seconds
# - None/bool: No action, continue with normal tick timing
OnTickResponse = Union["AnyIntent", int, float, None, bool]


class ScriptProtocol(Protocol):
    """
    Protocol for bot scripts.

    The script must implement an async on_tick method that returns:
    - AnyIntent: The intent will be sent to the server
    - int/float: Pause the next tick by this many seconds
    - None/bool: No action, continue with normal tick timing
    """

    async def on_tick(self) -> OnTickResponse: ...


CallableScript = Callable[[], Coroutine[Any, Any, OnTickResponse]]


@dataclass
class CallableScriptWrapper(ScriptProtocol):
    """
    Wrapper class for callable-based scripts.

    Allows setup_character to return a simple async function instead of a full script object.
    """

    _callable: CallableScript

    async def on_tick(self) -> OnTickResponse:
        return await self._callable()


@dataclass
class ConnectionEventResponse:
    items: dict[str, Any]
    constants: dict[str, Any]


@dataclass(kw_only=True)
class InstanceCharacter:
    character_id: str
    game_state: "GameState"
    instance: "Instance"
    _script: ScriptProtocol | None = None
    tick_time: float = 0.1
    units: dict[str, "AnyUnit"] = field(default_factory=dict)
    uniqueItems: dict[str, Any] = field(default_factory=dict)
    gameObjects: dict[str, "AnyGameObject"] = field(default_factory=dict)

    # Character-specific runtime data
    _tick_task: asyncio.Task[Any] | None = None
    last_intent_time: float = 0.0

    def handle_moved_event(self, event: events.MovedEvent) -> None:
        if unit := self.units.get(event.id):
            unit.position = Position(x=event.x, y=event.y)
        # else:
        #    logger.debug(f"Moved event error: {event.id} not found in units")

    def handle_calories_event(self, event: events.CaloriesEvent) -> None:
        if unit := self.units.get(event.unitId):
            unit.calories = event.calories
        else:
            logger.debug(f"Calories event error: {event.unitId} not found in units")

    def handle_hp_event(self, event: events.HpEvent) -> None:
        if unit := self.units.get(event.unitId):
            unit.hp = event.hp
        else:
            logger.debug(f"Hp event error: {event.unitId} not found in units")

    def handle_mp_event(self, event: events.MpEvent) -> None:
        if unit := self.units.get(event.unitId):
            unit.mp = event.mp
        else:
            logger.debug(f"Mp event error: {event.unitId} not found in units")

    def handle_unit_disappeared_event(self, event: events.UnitDisappearedEvent) -> None:
        self.units.pop(event.unitId, None)

    def handle_attacked_event(self, event: events.AttackedEvent) -> None:
        if attacker := self.units.get(event.attacker):
            attacker.tp = event.attackerTp
        else:
            logger.debug(f"Attacked event error: {event.attacker} not found in units")

        if attacked := self.units.get(event.attacked):
            attacked.hp = event.hp
        else:
            logger.debug(f"Attacked event error: {event.attacked} not found in units")

    def handle_unit_appeared_event(self, event: events.UnitAppearedEvent) -> None:
        self.units[event.unit.id] = event.unit
        # TODO: unique Items  # keys(event.uniqueItems).forEach((uniqueItemId) = > {  #    char.uniqueItems[uniqueItemId] = event.uniqueItems[uniqueItemId];  # });

    def handle_died_event(self, event: events.DiedEvent) -> None:
        if unit := self.units.get(event.unitId):
            unit.hp = 0

    def handle_despawn_event(self, event: events.DespawnEvent) -> None:
        self.units.pop(event.unitId, None)

    def handle_set_intent_event(self, event: events.SetIntentEvent) -> None:
        if unit := self.units.get(event.unitId):
            unit.intent = event.intent  # TODO: clearUnitActions
        else:
            logger.debug(f"SetIntent event error: {event.unitId} not found in units")

    def handle_loot_event(self, event: events.LootEvent) -> None:
        if unit := self.units.get(event.unitId):
            for item_id, amount in event.items.items():
                unit.inventory[item_id] = unit.inventory.get(item_id, 0) + amount
        else:
            logger.debug(f"Loot event error: {event.unitId} not found in units")

    def handle_inventory_event(self, event: events.InventoryEvent) -> None:
        if unit := self.units.get(event.unitId):
            for item_id, amount in event.inventory.items():
                if amount <= 0:
                    unit.inventory.pop(item_id, None)
                else:
                    unit.inventory[item_id] = amount
        else:
            logger.debug(f"Inventory event error: {event.unitId} not found in units")

    def handle_object_appeared_event(self, event: events.ObjectAppearedEvent) -> None:
        self.gameObjects[event.object.id] = event.object

    def handle_object_disappeared_event(self, event: events.ObjectDisappearedEvent) -> None:
        try:
            del self.gameObjects[event.objectId]
        except KeyError:
            logger.debug(f"ObjectDisappeared event error: {event.objectId} not found in gameObjects")

    def handle_ate_event(self, event: events.AteEvent) -> None:
        if unit := self.units.get(event.unitId):
            if hasattr(unit, "calories"):
                unit.calories = event.calories
            if hasattr(unit, "inventory"):
                unit.inventory[event.item] = event.remaining
        else:
            logger.debug(f"Ate event error: {event.unitId} not found in units")

    def handle_connection_event(self, event: events.ConnectionEvent) -> ConnectionEventResponse:
        assert self.character_id == event.player.id

        self.units = event.units
        self.game_state.units = event.units
        self.gameObjects = event.gameObjects

        # TODO: uniqueItems
        # TODO: gameObjects

        logger.success(f"Game state initialized for player: {event.player.id}")
        return ConnectionEventResponse(event.items, event.constants)

    def handle_accepted_quest_event(self, event: events.AcceptedQuestEvent) -> None:
        logger.success(f"Quest accepted: {event.quest.name} ({event.quest.id}) for unit: {event.unitId}")
        if player := self.game_state.player:
            player.quests[event.quest.id] = event.quest
        if self.character_id == event.unitId and (npc := self.game_state.units.get(event.quest.start_npc)):
            npc.availableQuests.pop(event.quest.id, None)

    def handle_quest_started_event(self, event: events.QuestStartedEvent) -> None:
        logger.success(f"Quest started: {event.quest} from NPC: {event.npc}")

    def handle_quest_completed_event(self, event: events.QuestCompletedEvent) -> None:
        if unit := self.units.get(event.unitId):
            unit.quests.pop(event.questId, None)

    def handle_quest_progress_event(self, event: events.QuestProgressEvent) -> None:
        logger.info(f"Quest progress: {event.quest} - {event.objective}: {event.current}/{event.target}")

    def handle_quest_failed_event(self, event: events.QuestFailedEvent) -> None:
        logger.warning(f"Quest failed: {event.quest} - Reason: {event.reason}")

    def handle_quest_abandoned_event(self, event: events.QuestAbandonedEvent) -> None:
        logger.info(f"Quest abandoned: {event.quest}")

    def handle_quest_update_event(self, event: events.QuestUpdateEvent) -> None:
        if unit := self.game_state.player:
            if unit.id == event.unitId:
                unit.quests[event.quest.id] = event.quest

    def handle_focus_event(self, event: events.FocusEvent) -> None:
        if unit := self.units.get(event.monsterId):
            if isinstance(unit, Monster):
                unit.focus = event.focus
            else:
                logger.error(f"Focus event error: {unit} {event.monsterId} is not a monster")
        else:
            logger.debug(f"Focus event error: {event.monsterId} not found in units")

    def handle_stats_event(self, event: events.StatsEvent) -> None:
        if unit := self.units.get(event.unitId):
            if hasattr(unit, "stats"):
                unit.stats = event.stats


@dataclass
class Instance:
    instance_id: str
    time: int = 0
    characters: dict[str, InstanceCharacter] = field(default_factory=dict)
    playersSeekingParty: dict[str, str] = field(default_factory=dict)
