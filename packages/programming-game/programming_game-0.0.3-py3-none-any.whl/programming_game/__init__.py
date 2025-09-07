import contextlib

from .client import GameClient
from .intents import *  # noqa: F403
from .schema.events import *  # noqa: F403
from .schema.instance_character import OnTickResponse
from .schema.units import GameState

with contextlib.suppress(ImportError):
    from . import db

__all__ = [  # noqa: F405
    # Intents
    "AbandonQuestIntent",
    "AcceptPartyEventIntent",
    "AcceptQuestIntent",
    "AttackIntent",
    "BaseIntent",
    "BuyIntent",
    "BuyItemsIntent",
    "CastSpellIntent",
    "CraftIntent",
    "DeclinePartyEventIntent",
    "DepositIntent",
    "DropIntent",
    "EatIntent",
    "EquipIntent",
    "EquipSpellIntent",
    "InviteToPartyIntent",
    "LeavePartyIntent",
    "MoveIntent",
    "RespawnIntent",
    "SellItemsIntent",
    "SetRoleIntent",
    "SetTradeIntent",
    "TurnInQuestIntent",
    "UnEquipIntent",
    "UnequipSpellIntent",
    "UseIntent",
    "UseWeaponSkillIntent",
    "WeaponSkillIntent",
    "WithdrawIntent",
    "AnyIntent",
    "SendIntentValue",
    "SendIntent",
    # Events
    "ArenaEvent",
    "AteEvent",
    "AttackedEvent",
    "BeganCastingEvent",
    "BeganEquippingSpellEvent",
    "CaloriesEvent",
    "CastSpellEvent",
    "ConnectionEvent",
    "DespawnEvent",
    "DiedEvent",
    "DroppedEvent",
    "EquippedSpellEvent",
    "AnyEvent",
    "HpEvent",
    "LootEvent",
    "MovedEvent",
    "MpEvent",
    "QuestStartedEvent",
    "QuestCompletedEvent",
    "QuestProgressEvent",
    "QuestFailedEvent",
    "QuestAbandonedEvent",
    "QuestUpdateEvent",
    "SetIntentEvent",
    "StorageChargedEvent",
    "UnequippedSpellEvent",
    "UsedWeaponSkillEvent",
    "UnitAppearedEvent",
    "UnitDisappearedEvent",
    "UpdatedTradeEvent",
    # Client
    "GameClient",
    # Units
    "GameState",
    # Responses
    "OnTickResponse",
]
