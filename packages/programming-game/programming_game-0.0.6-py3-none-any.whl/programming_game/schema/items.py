import msgspec


class Item(msgspec.Struct, tag=True, kw_only=True, repr_omit_defaults=True, omit_defaults=True):
    """Represents an item."""
    id: str
    name: str
    weight: float
    calories: float | None = None
    buyFromVendorPrice: float
    sellToVendorPrice: float
    deprecated: bool = False


class Trash(Item, tag="trash"):
    """Represents a trash item."""
    pass


class Ammo(Item, tag="ammo"):
    """Represents a ammo item."""
    pass


class Usable(Item, tag="usable"):
    """Represents a usable item."""
    pass


class Food(Item, tag="food"):
    """Represents a food item."""
    pass


class Equipments(Item):
    pass


class Weapon(Equipments):
    spellCount: int
    stats: dict[str, float]  # Fixme


class OffhandWeapon(Equipments):
    pass


class Accessories(Equipments):
    pass


class Amulet(Accessories, tag="amulet"):
    pass


class Ring(Accessories, tag="ring"):
    pass


class Armor(Equipments):
    pass


class Helm(Armor, tag="helm"):
    pass


class Chest(Armor, tag="chest"):
    pass


class Legs(Armor, tag="legs"):
    pass


class Boots(Armor, tag="feet"):
    pass


class Gloves(Armor, tag="hands"):
    pass


class Pickaxe(Weapon, tag="pickaxe"):
    """Represents a Pickaxe."""


class FellingAxe(Weapon, tag="fellingAxe"):
    """Represents a FellingAxe."""


class OneHandedSword(Weapon, tag="oneHandedSword"):
    """Represents a OneHandedSword."""
    pass


class TwoHandedSword(Weapon, tag="twoHandedSword"):
    """Represents a TwoHandedSword."""


class Staff(Weapon, tag="staff"):
    """Represents a Staff item."""
    pass


class Dagger(Weapon, tag="dagger"):
    """Represents a Dagger item."""
    pass


class WeaponTool(Weapon):
    pass


class Shield(Equipments, tag="shield"):
    """Represents a Shield item."""


class Bow(Weapon, tag="bow"):
    pass


class CrossBow(Weapon, tag="crossbow"):
    pass


class Grimmoire(Weapon, tag="grimmoire"):
    pass


EquipmentT = Helm | Chest | Legs | Boots | Gloves | Amulet | Ring | Shield
WeaponT = Staff | Dagger | OneHandedSword | Pickaxe | FellingAxe | TwoHandedSword | Bow | CrossBow | Grimmoire

AnyItem = Trash | Usable | Food | Ammo | Weapon | WeaponT | EquipmentT
