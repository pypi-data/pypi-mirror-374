from typing import Any

import msgspec

from .game_object import AnyGameObject
from .intents import AnyIntent
from .other import PlayerStats, UnitTrades
from .quest import AvailableQuest, ActiveQuest
from .units import AnyUnit, Player


class BaseEvent(msgspec.Struct, forbid_unknown_fields=True, tag=True):
    pass


class AteEvent(BaseEvent, tag="ate"):
    unitId: str
    item: str
    calories: float
    remaining: int


class AttackedEvent(BaseEvent, tag="attacked"):
    attacker: str
    attacked: str
    damage: float
    hp: float
    attackerTp: float


class CaloriesEvent(BaseEvent, tag="calories"):
    unitId: str
    calories: float


class ConnectionEvent(BaseEvent, forbid_unknown_fields=False, tag="connectionEvent", kw_only=True):
    player: Player
    party: dict[str, bool]
    units: dict[str, AnyUnit]
    gameObjects: dict[str, AnyGameObject]
    playersSeekingParty: list[str]  # PlayersSeekingParty
    time: int
    items: dict[str, Any] | None = None
    constants: dict[str, Any] | None = None


class DespawnEvent(BaseEvent, tag="despawn"):
    unitId: str


class DiedEvent(BaseEvent, tag="died"):
    unitId: str


class FocusEvent(BaseEvent, tag="focus"):
    focus: str
    monsterId: str


class HpEvent(BaseEvent, tag="hp"):
    unitId: str
    hp: float


class LootEvent(BaseEvent, tag="loot"):
    unitId: str
    items: dict[str, int]


class MovedEvent(BaseEvent, tag="moved"):
    id: str
    x: float
    y: float


class MpEvent(BaseEvent, tag="mp"):
    unitId: str
    mp: float


class ObjectAppearedEvent(BaseEvent, tag="objectAppeared"):
    object: AnyGameObject


class ObjectDisappearedEvent(BaseEvent, tag="objectDisappeared"):
    objectId: str


class SetIntentEvent(BaseEvent, tag="setIntent"):
    unitId: str
    intent: AnyIntent | None


class StatsEvent(BaseEvent, tag="stats"):
    unitId: str
    stats: PlayerStats


class TpEvent(BaseEvent, tag="tp"):
    unitId: str
    tp: float


class UnitAppearedEvent(BaseEvent, tag="unitAppeared"):
    unit: AnyUnit
    uniqueItems: dict[str, Any]


class UnitDisappearedEvent(BaseEvent, tag="unitDisappeared"):
    unitId: str


class UpdatedTradeEvent(BaseEvent, tag="updatedTrade"):
    unitId: str
    trades: UnitTrades


class StorageChargedEvent(BaseEvent, tag="storageCharged"):
    coinsLeft: int
    charged: int


class DepositedEvent(BaseEvent, tag="deposited"):
    items: dict[str, int]


class WithdrewEvent(BaseEvent, tag="withdrew"):
    items: dict[str, int]


class StorageEmptiedEvent(BaseEvent, tag="storageEmptied"):
    pass


class ArenaEvent(BaseEvent, tag="arena"):
    duration: int


class BeganCastingEvent(BaseEvent, tag="beganCasting"):
    unitId: str
    spell: str
    target: str | None = None
    duration: int | None = None


class CastSpellEvent(BaseEvent, tag="castSpell"):
    unitId: str
    spell: str


class BeganEquippingSpellEvent(BaseEvent, tag="beganEquippingSpell"):
    unitId: str
    spell: str
    duration: int


class UnequippedSpellEvent(BaseEvent, tag="unequippedSpell"):
    unitId: str


class UsedWeaponSkillEvent(BaseEvent, tag="usedWeaponSkill"):
    unitId: str
    targetId: str
    skill: str
    tp: float


class EquippedSpellEvent(BaseEvent, tag="equippedSpell"):
    unitId: str
    spell: str


class SpellCastedEvent(BaseEvent, tag="spellCasted"):
    unitId: str
    spell: str
    target: str | None = None
    damage: float | None = None
    heal: float | None = None


class SpellFailedEvent(BaseEvent, tag="spellFailed"):
    unitId: str
    spell: str
    reason: str | None = None


class SpellInterruptedEvent(BaseEvent, tag="spellInterrupted"):
    unitId: str
    spell: str
    reason: str | None = None


class DroppedEvent(BaseEvent, tag="dropped"):
    unitId: str
    item: str
    amount: int


class InventoryEvent(BaseEvent, tag="inventory"):
    unitId: str
    inventory: dict[str, int]


class AcceptedQuestEvent(BaseEvent, tag="acceptedQuest"):
    unitId: str
    quest: ActiveQuest


class QuestCompletedEvent(BaseEvent, tag="completedQuest"):
    unitId: str
    questId: str
    questName: str


class QuestUpdateEvent(BaseEvent, tag="questUpdate"):
    unitId: str
    quest: ActiveQuest


class QuestAvailableEvent(BaseEvent, tag="questAvailable"):
    npcId: str
    quest: AvailableQuest


AnyEvent = (
        AcceptedQuestEvent
        | ArenaEvent
        | AteEvent
        | AttackedEvent
        | BeganCastingEvent
        | BeganEquippingSpellEvent
        | CaloriesEvent
        | CastSpellEvent
        | ConnectionEvent
        | DepositedEvent
        | DespawnEvent
        | DiedEvent
        | DroppedEvent
        | EquippedSpellEvent
        | FocusEvent
        | HpEvent
        | InventoryEvent
        | LootEvent
        | MovedEvent
        | MpEvent
        | ObjectAppearedEvent
        | ObjectDisappearedEvent
        | QuestAvailableEvent
        | QuestCompletedEvent
        | QuestUpdateEvent
        | SetIntentEvent
        | SpellCastedEvent
        | SpellFailedEvent
        | SpellInterruptedEvent
        | StatsEvent
        | StorageChargedEvent
        | StorageEmptiedEvent
        | TpEvent
        | UnequippedSpellEvent
        | UsedWeaponSkillEvent
        | UnitAppearedEvent
        | UnitDisappearedEvent
        | UpdatedTradeEvent
        | WithdrewEvent
)
