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

