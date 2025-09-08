import msgspec

from .position import Position


class BaseGameObject(msgspec.Struct, forbid_unknown_fields=True, tag=True):
    position: Position
    id: str
    radius: float
    label: str


class MiningNode(BaseGameObject, tag="miningNode"):
    oreType: str


class Tree(BaseGameObject, tag="tree"):
    treeType: str
    pass


AnyGameObject = Tree | MiningNode
