import msgspec

from programming_game.schema.other import InventoryType
from programming_game.schema.position import Position


class BaseIntent(msgspec.Struct, tag=True, forbid_unknown_fields=True):
    pass


class AbandonQuestIntent(BaseIntent, tag="abandonQuest"):
    quest: str


class AcceptPartyEventIntent(BaseIntent, tag="acceptPartyInvite"):
    inviter: str


class AcceptQuestIntent(BaseIntent, tag="acceptQuest"):
    questId: str
    npcId: str


class AttackIntent(BaseIntent, tag="attack"):
    target: str


class BuyIntent(BaseIntent, tag="buy"):
    items: dict[str, int]
    from_: str = msgspec.field(name="from")


class BuyItemsIntent(BaseIntent, tag="buyItems"):
    items: dict[str, int]
    from_: str = msgspec.field(name="from")


class CastSpellIntent(BaseIntent, tag="cast"):
    spell: str
    target: str


class CraftIntent(BaseIntent, tag="craft"):
    item: str
    from_: dict[str, int] = msgspec.field(name="from")


class DeclinePartyEventIntent(BaseIntent, tag="declinePartyInvite"):
    inviter: str


class DepositIntent(BaseIntent, tag="deposit"):
    npcId: str
    until: InventoryType


class DropIntent(BaseIntent, tag="drop"):
    item: str
    until: int


class EatIntent(BaseIntent, tag="eat"):
    item: str
    save: int


class EquipIntent(BaseIntent, tag="equip"):
    item: str
    slot: str  # TODO: einschränken


class EquipSpellIntent(BaseIntent, tag="equipSpell"):
    spell: str


class UnequipSpellIntent(BaseIntent, tag="unequipSpell"):
    pass


class InviteToPartyIntent(BaseIntent, tag="inviteToParty"):
    target: str


class LeavePartyIntent(BaseIntent, tag="leaveParty"):
    pass


class MoveIntent(BaseIntent, tag="move"):
    position: Position


class RespawnIntent(BaseIntent, tag="respawn"):
    pass


class SellItemsIntent(BaseIntent, tag="sellItems"):
    items: InventoryType
    to: str


class SetRoleIntent(BaseIntent, tag="setRole"):
    role: str


class SetTradeIntent(BaseIntent, tag="setTrade"):
    buying: dict[str, dict[str, int]]
    selling: dict[str, dict[str, int]]


class TurnInQuestIntent(BaseIntent, tag="turnInQuest"):
    npcId: str
    questId: str


class UnEquipIntent(BaseIntent, tag="unequip"):
    slot: str  # TODO: einschränken


class UseIntent(BaseIntent, tag="use"):
    item: str
    until: int
    target: str | None = None


class UseWeaponSkillIntent(BaseIntent, tag="useWeaponSkill"):
    skill: str
    target: str


class WeaponSkillIntent(BaseIntent, tag="weaponSkill"):
    skill: str
    target: str


class WithdrawIntent(BaseIntent, tag="withdraw"):
    from_: str
    items: InventoryType


AnyIntent = (
        AbandonQuestIntent
        | AcceptPartyEventIntent
        | AcceptQuestIntent
        | AttackIntent
        | BuyIntent
        | BuyItemsIntent
        | CastSpellIntent
        | CraftIntent
        | DeclinePartyEventIntent
        | DepositIntent
        | DropIntent
        | EatIntent
        | EquipIntent
        | EquipSpellIntent
        | InviteToPartyIntent
        | LeavePartyIntent
        | MoveIntent
        | RespawnIntent
        | SellItemsIntent
        | SetRoleIntent
        | SetTradeIntent
        | TurnInQuestIntent
        | UnEquipIntent
        | UnequipSpellIntent
        | UseIntent
        | UseWeaponSkillIntent
        | WeaponSkillIntent
        | WithdrawIntent
)
"""Ein Typ-Alias, der jede mögliche Aktion (Intent) im System repräsentiert."""


class SendIntentValue(msgspec.Struct):
    c: str
    i: str
    unitId: str
    intent: AnyIntent | None


class SendIntent(msgspec.Struct):
    value: SendIntentValue
    type: str = "setIntent"
