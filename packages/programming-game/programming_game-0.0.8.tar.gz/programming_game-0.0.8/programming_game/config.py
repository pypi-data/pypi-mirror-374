import os

import msgspec
from dotenv import dotenv_values


class ProgrammingGameConfig(msgspec.Struct, kw_only=True):
    DEBUG_MODE: bool = False
    SERVER_URL: str = "wss://programming-game.com"
    GAME_CLIENT_ID: str = "GAME_CLIENT_ID"
    GAME_CLIENT_KEY: str = "GAME_CLIENT_KEY"
    DATABASE_URL: str | None = None
    DISABLE_LOOP: bool = False
    FAST_LOOP_DELAY: float = 0.1  # loop pause after no intent was sent to the server
    SLOW_LOOP_DELAY: float = 0.3   # loop pause after an intent was sent to the server
    ERROR_LOOP_DELAY: float = 1.0  # loop pause after an error occurred

def load_config(**kwargs) -> ProgrammingGameConfig:
    config = {
        **dotenv_values(".env"),
        **os.environ,
        **{k.upper(): v for k, v in kwargs.items() if v},
    }
    return msgspec.convert(config, type=ProgrammingGameConfig, strict=False)
