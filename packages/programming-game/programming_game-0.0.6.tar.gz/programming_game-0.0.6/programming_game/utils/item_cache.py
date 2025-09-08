from typing import Protocol

import msgspec

from programming_game.schema.items import AnyItem


class ItemCacheStorage(msgspec.Struct):
    server_version: str
    items: dict[str, AnyItem]
    constants: dict[str, float | int | str]


class ItemStorageMixinProtocol(Protocol):
    _items: dict[str, AnyItem]
    _server_version: str | None
    _client_version: str | None


class ItemStorageMixin:
    def load_items_and_constants(self: ItemStorageMixinProtocol):
        with open("item_cache.yaml", "rb") as f:
            data = f.read()
        item_cache = msgspec.yaml.decode(data, type=ItemCacheStorage)
        self._items = item_cache.items
        self._constants = item_cache.constants
        self._client_version = item_cache.server_version

    def set_items_and_constants(self: ItemStorageMixinProtocol, items: dict[str, AnyItem],
                                constants: dict[str, float | int | str]):
        self._items = items
        self._constants = constants

        if not self._server_version:
            raise ValueError("server_version not set")

        item_cache = ItemCacheStorage(server_version=self._server_version, items=items, constants=constants)
        data = msgspec.yaml.encode(item_cache)
        with open("item_cache.yaml", "wb") as f:
            f.write(data)
