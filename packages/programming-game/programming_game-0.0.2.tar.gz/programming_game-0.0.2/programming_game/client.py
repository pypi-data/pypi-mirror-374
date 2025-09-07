import asyncio
import importlib
import inspect
import time
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any, get_args

import msgspec
import websockets
import websockets.protocol

if TYPE_CHECKING:
    from .db import DBClient

from collections import defaultdict

from programming_game.intents import AnyIntent, BaseIntent, SendIntent, SendIntentValue

from .logging import logger
from .schema.events import AnyEvent
from .schema.instance_character import (
    CallableScriptWrapper,
    ConnectionEventResponse,
    Instance,
    InstanceCharacter,
    OnTickResponse,
)
from .schema.messages import EventsMessage, ServerMessage, VersionMessage
from .schema.units import GameState
from .utils import to_snake_case

try:
    from .db import DBClient

    _db_available = True
except ImportError:
    DBClient = type(None)  # type: ignore
    _db_available = False

SERVER_URL = "wss://programming-game.com"

json_decoder = msgspec.json.Decoder()
json_encoder = msgspec.json.Encoder()

OnLoopHandler = Callable[[GameState], Coroutine[Any, Any, AnyIntent | None]]
OnEventHandler = Callable[[dict[str, Any]], Coroutine[Any, Any, None]]
OnLoopHandlerWithEvents = Callable[[GameState, list[AnyEvent]], Coroutine[Any, Any, AnyIntent | None]]


CallableScript = Callable[[], Coroutine[Any, Any, OnTickResponse]]
OnSetupCharacter = Callable[[GameState], Coroutine[Any, Any, Any | CallableScript]]


# noinspection PyPep8Naming
class GameClient:
    """
    Represents a game client responsible for connecting to game servers and managing
    real-time interactions such as events, state updates, and communication with
    instances and characters.

    The `GameClient` class provides functionality to manage websocket connections,
    handle messages sent from the game server, register event handlers, and execute
    custom logic in game loops. It acts as the client layer for interacting with
    a game environment.

    :ivar credentials: Credentials for authenticating with the server.
    :type credentials: dict[str, str] | None
    :ivar log_level: Logging level to use for the client.
    :type log_level: str
    """

    def __init__(
        self,
        credentials: dict[str, str] | None = None,
        log_level: str = "INFO",
        enable_db: bool = False,
        database_url: str | None = None,
    ):
        self._credentials = credentials
        self._log_level = log_level
        self._websocket: websockets.WebSocketClientProtocol | None = None  # type: ignore
        self._time = 0
        self._instances: dict[str, Instance] = {}
        self._items: Any = {}
        self._constants: Any = {}
        self._is_running = False
        self._reconnect_delay = 1

        self._setup_character_handler: dict | None = None
        self._on_event_handlers: dict[type, list[OnEventHandler]] = defaultdict(list)

        # Optional DB integration
        self._db_client: DBClient | None = None
        if enable_db and _db_available:
            self._db_client = DBClient(database_url)
        elif enable_db and not _db_available:
            logger.warning(
                "DB integration requested but dependencies not installed. Install with: pip install programming-game[db]"
            )

    def setup_character(self) -> Callable[[OnSetupCharacter], OnSetupCharacter]:
        def decorator(func: OnSetupCharacter) -> OnSetupCharacter:
            sig = inspect.signature(func)
            params = list(sig.parameters.values())
            is_instance_method = params and params[0].name == "self"
            class_name = None
            module = None
            if is_instance_method:
                qualname = func.__qualname__
                class_name = qualname.rsplit(".", 1)[0]
                module = func.__module__
            self._setup_character_handler = {
                "func": func,
                "is_instance_method": is_instance_method,
                "class_name": class_name,
                "module": module,
            }
            logger.debug(f"✅ Funktion '{func.__name__}' registriert")
            return func

        return decorator

    def on_event(self, event_type: type | tuple | list):
        def decorator(func: OnEventHandler) -> OnEventHandler:
            extracted_types = get_args(event_type)
            types_to_register = []

            if extracted_types:
                types_to_register = list[Any](extracted_types)
            elif isinstance(event_type, list | tuple):
                types_to_register = event_type
            else:
                types_to_register = [event_type]

            for etype in types_to_register:
                if inspect.isclass(etype):
                    self._on_event_handlers[etype].append(func)
                    logger.debug(f"✅ Funktion '{func.__name__}' registriert für Event '{etype.__name__}'")
                else:
                    logger.warning(f"⚠️ Warnung: '{etype}' ist kein gültiger Typ und wird ignoriert.")
            return func

        return decorator

    # DB integration methods
    async def get_db_session(self) -> Any:
        """Get a database session for user operations."""
        if self._db_client:
            return await self._db_client.get_session()
        else:
            raise RuntimeError("Database integration not enabled. Set enable_db=True in constructor.")

    async def queue_event(self, event_data: dict[str, Any], user_id: str | None = None):
        """Queue a user-defined event for logging to database."""
        if self._db_client:
            await self._db_client.queue_user_event(event_data, user_id)
        else:
            logger.warning("Database integration not enabled. Event not queued.")

    async def _initialize_instance(self, instance_id: str, character_id: str) -> InstanceCharacter:
        instance = self._instances.get(instance_id)
        if not instance:
            instance = Instance(time=0, instance_id=instance_id)
            self._instances[instance_id] = instance
        if character_id not in instance.characters:
            game_state = GameState(instance_id=instance_id, character_id=character_id)
            if self._setup_character_handler:
                if self._setup_character_handler["is_instance_method"]:
                    class_name = self._setup_character_handler["class_name"]
                    module = self._setup_character_handler["module"]
                    mod = importlib.import_module(module)
                    cls = getattr(mod, class_name)
                    if not hasattr(self, "_setup_instance"):
                        self._setup_instance = cls()
                    script = await self._setup_character_handler["func"](self._setup_instance, game_state)
                else:
                    script = await self._setup_character_handler["func"](game_state)
            else:
                script = None

            if not script:
                character = InstanceCharacter(
                    character_id=character_id, instance=instance, game_state=game_state
                )
                instance.characters[character_id] = character
                logger.warning("Created character without script. Not starting character task!")
            elif hasattr(script, "on_tick"):
                # Traditional script object
                character = InstanceCharacter(
                    _script=script, character_id=character_id, instance=instance, game_state=game_state
                )
                instance.characters[character_id] = character
                self._start_character_task(instance_id, character_id)
            elif callable(script):
                # New callable-based script
                wrapped_script = CallableScriptWrapper(_callable=script)
                character = InstanceCharacter(
                    _script=wrapped_script,
                    character_id=character_id,
                    instance=instance,
                    game_state=game_state,
                )
                instance.characters[character_id] = character
                self._start_character_task(instance_id, character_id)
            else:
                logger.warning(
                    f"Failed to setup character {character_id} in instance {instance_id}. "
                    f"Expected script object or callable, got {type(script)}. Not starting character task!"
                )

        return instance.characters[character_id]

    def _start_character_task(self, instance_id: str, character_id: str) -> None:
        """Start or restart a character tick task."""
        instance = self._instances.get(instance_id)
        if not instance or character_id not in instance.characters:
            logger.warning(f"Cannot start task for unknown character {character_id} in {instance_id}")
            return

        character = instance.characters[character_id]

        # Cancel existing task if any
        if character._tick_task and not character._tick_task.done():
            character._tick_task.cancel()

        # Only create task if websocket is connected (has running event loop)
        if self._websocket and self._websocket.state == websockets.protocol.State.OPEN:
            # Create new task
            task = asyncio.create_task(self._character_tick_loop(instance_id, character_id))
            character._tick_task = task

            def log_task_exception(task: asyncio.Task[Any]):
                if not task.cancelled() and (exc := task.exception()):
                    logger.error(
                        f"Character tick task for {character_id} in {instance_id} ended unexpectedly!",
                        exc_info=exc,
                    )

            task.add_done_callback(log_task_exception)
            logger.debug(f"Started tick task for character {character_id} in instance {instance_id}")
        else:
            # Just mark that we need to start this task when websocket connects
            character._tick_task = None  # Placeholder
            logger.debug(f"Queued tick task for character {character_id} in instance {instance_id}")

    async def _send(self, message: dict[str, Any]):
        if self._websocket:
            msg_str = json_encoder.encode(message).decode("utf-8")
            # logger.debug(f"Sending message: {msg_str}")
            await self._websocket.send(msg_str)

    async def _send_msg(self, data: msgspec.Struct):
        if self._websocket:
            msg_str = json_encoder.encode(data).decode("utf-8")
            # logger.debug(f"message: {msg_str}")
            await self._websocket.send(msg_str)

    async def _update_state(self, character_instance: InstanceCharacter, event_list: list[AnyEvent]):
        char_id = character_instance.character_id
        instance_id = character_instance.instance.instance_id

        for event in event_list:
            event_type = type(event)
            handler_name = "handle_" + to_snake_case(event_type.__name__)

            if cb := getattr(character_instance, handler_name, None):
                result = cb(event)
                if result and result is ConnectionEventResponse:
                    self._items = result.items
                    self._constants = result.constants
            else:
                logger.warning(f"missing {handler_name}")

            if event_type in self._on_event_handlers:
                for handler in self._on_event_handlers[event_type]:
                    try:
                        await handler(event, character_instance.game_state)
                    except Exception:
                        logger.error(
                            f"An error occurred in the on_event callback for event: {event_type.__name__}",
                            exc_info=True,
                        )

            # Collect events for on_loop handler if they match specified types
            # if self._on_loop_event_types and event_type in self._on_loop_event_types:
            #    character_instance.recent_events.append(event)

            # Log incoming event to database
            if self._db_client:
                try:
                    await self._db_client.log_event(
                        event_type=event_type.__name__,
                        direction="in",
                        data=msgspec.to_builtins(event),
                        character_id=char_id,
                        instance_id=instance_id,
                        user_id=self._credentials.get("id") if self._credentials else None,
                    )
                except Exception:
                    logger.error(f"Failed to log incoming event: {event_type.__name__}", exc_info=True)

    async def _character_tick_loop(self, instance_id: str, char_id: str):
        """Per-character tick loop with dynamic sleep intervals."""
        instance = self._instances.get(instance_id)
        if not instance or char_id not in instance.characters:
            logger.debug(f"Character {char_id} in instance {instance_id} no longer exists")
            return

        character = instance.characters[char_id]

        while self._websocket and self._websocket.state == websockets.protocol.State.OPEN:
            try:
                instance = self._instances.get(instance_id)
                if not instance or char_id not in instance.characters:
                    logger.debug(f"Character {char_id} in instance {instance_id} no longer exists")
                    break

                character_state = instance.characters[char_id]
                if instance_id == "overworld" or instance_id.startswith("instance-"):
                    units = character_state.units
                    if char_id not in units:
                        logger.debug(f"Character {char_id} not found in units in loop")
                        await asyncio.sleep(1)
                        continue

                    char = units[char_id]
                    try:
                        result: OnTickResponse = await character_state._script.on_tick()

                        if isinstance(result, BaseIntent):
                            # Send intent to server
                            if result == char.intent:
                                # Same intent, no need to send
                                pass
                            else:
                                player_name = (
                                    character.game_state.player.name
                                    if character.game_state.player
                                    else "Unknown"
                                )
                                logger.debug(
                                    f"{player_name} {time.time() - character.last_intent_time:.2f} Sending intent for {char_id}: {result}"
                                )

                                # Log outgoing intent to database
                                if self._db_client:
                                    try:
                                        await self._db_client.log_intent(
                                            intent_type=type(result).__name__,
                                            data=msgspec.to_builtins(result),
                                            character_id=char_id,
                                            instance_id=instance_id,
                                            user_id=self._credentials.get("id")
                                            if self._credentials
                                            else None,
                                        )
                                    except Exception:
                                        logger.error(
                                            f"Failed to log outgoing intent: {type(result).__name__}",
                                            exc_info=True,
                                        )

                                await self._send_msg(
                                    SendIntent(
                                        value=SendIntentValue(
                                            c=char_id, i=instance_id, unitId=char_id, intent=result
                                        )
                                    )
                                )
                                # Update last intent time
                                character.last_intent_time = time.time()
                                # Ensure minimum 0.3s pause after sending intent
                                await asyncio.sleep(max(character_state.tick_time, 0.3))
                                continue
                        elif isinstance(result, int | float):
                            # Custom pause duration
                            logger.debug(
                                f"{char_id} {time.time() - character.last_intent_time:.2f} Reschedule for {result}s"
                            )
                            await asyncio.sleep(result)
                            continue
                        # None or bool: no special action, continue with normal flow

                    except Exception as e:
                        logger.error(f"Error in on_loop_handler for {char_id}: {e}", exc_info=True)
                    finally:
                        # Clear recent events after processing
                        # character.recent_events.clear()
                        pass

                # No intent sent, use normal sleep
                await asyncio.sleep(character_state.tick_time)

            except Exception:
                logger.error(
                    f"An error occurred in character tick loop for {char_id} (probably in your on_tick logic). Pausing for 5 seconds.",
                    exc_info=True,
                )
                await asyncio.sleep(5)

    async def handle_message(self, message: ServerMessage) -> None:
        try:
            if type(message) is EventsMessage:
                for instance_id, chars in message.value.items():
                    for char_id, events in chars.items():
                        character_instance = await self._initialize_instance(instance_id, char_id)
                        await self._update_state(character_instance, events)
            elif type(message) is VersionMessage:
                logger.info(f"Server version: {message.value}")
        except Exception as e:
            logger.error(f"Error in handle_message: {e}", exc_info=True)

    async def parse_message(self, message_str: str) -> None:
        message = json_decoder.decode(message_str)
        try:
            if message.get("type") == "events":
                for _instance_id, chars in message.get("value", {}).items():
                    for char_id, events in chars.items():
                        replace = []
                        for event in events:
                            # if there is a invalid intent in the event, remove it
                            if event[0] == "connectionEvent":
                                for unit in event[1].get("units", []).values():
                                    if unit["intent"]:
                                        try:
                                            msgspec.convert(unit["intent"], type=AnyIntent)
                                        except msgspec.ValidationError:
                                            unit["intent"] = None
                            # check all events
                            event[1]["type"] = event[0]
                            try:
                                msgspec.convert(event[1], type=AnyEvent)
                                replace.append(event[1])
                            except msgspec.ValidationError as e:
                                del event[1]["type"]
                                logger.warning(
                                    f"Error deconding event: {char_id} {event[0]} {e} {event[1]}",
                                    exc_info=False,
                                )
                                1
                        chars[char_id] = replace
        except Exception as e:
            logger.error(f"Error in parse_message: {e}", exc_info=True)
            return
        try:
            message = msgspec.convert(message, type=ServerMessage)
        except msgspec.ValidationError:
            logger.error(f"Invalid message: {message}", exc_info=True)
            return
        await self.handle_message(message)

    async def connect(self):
        if not self._setup_character_handler:
            raise RuntimeError(
                "No setup_character handler registered. Use @client.setup_character decorator."
            )

        self._is_running = True

        # Initialize DB if enabled
        if self._db_client:
            await self._db_client.initialize()

        while self._is_running:
            logger.info(f"Connecting to server at {SERVER_URL}...")
            try:
                async with websockets.connect(SERVER_URL) as websocket:
                    self._websocket = websocket
                    self._reconnect_delay = 1  # Reset reconnect delay on successful connection
                    logger.success("Connection established successfully!")
                    await self._send(
                        {
                            "type": "credentials",
                            "value": self._credentials,
                            "version": "0.0.1",
                        }
                    )

                    # Start tick tasks for existing characters
                    for instance_id, instance in self._instances.items():
                        for char_id in instance.characters:
                            self._start_character_task(instance_id, char_id)

                    # Also start any queued tasks (characters with tick_task = None)
                    for instance_id, instance in self._instances.items():
                        for char_id, character in instance.characters.items():
                            if character._tick_task is None:  # Queued task
                                self._start_character_task(instance_id, char_id)

                    async for message_str in websocket:
                        await self.parse_message(message_str)

            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"Connection closed: {e}. Reconnecting in {self._reconnect_delay} seconds...")
            except ConnectionRefusedError:
                logger.error(f"Connection refused. Reconnecting in {self._reconnect_delay} seconds...")
            except Exception:
                logger.error(
                    f"A critical error occurred. Reconnecting in {self._reconnect_delay} seconds...",
                    exc_info=True,
                )
            finally:
                # Cancel all character tasks on disconnect
                for instance in self._instances.values():
                    for character in instance.characters.values():
                        if character._tick_task and not character._tick_task.done():
                            character._tick_task.cancel()
                        # Reset runtime data
                        character._tick_task = None
                        character.last_intent_time = 0.0
                        # character.recent_events.clear()

                self._websocket = None
                if self._is_running:
                    await asyncio.sleep(self._reconnect_delay)
                    self._reconnect_delay = min(self._reconnect_delay * 2, 60)  # Exponential backoff, max 60s

    async def disconnect(self) -> None:
        """Gracefully disconnects from the server."""
        # logger.info("Disconnecting from server...")
        self._is_running = False

        # Cancel all character tasks
        for instance in self._instances.values():
            for character in instance.characters.values():
                if character._tick_task and not character._tick_task.done():
                    character._tick_task.cancel()
                # Reset runtime data
                character._tick_task = None
                character.last_intent_time = 0.0
                # character.recent_events.clear()

        if self._websocket and self._websocket.state == websockets.protocol.State.OPEN:
            await self._websocket.close()
        self._websocket = None

        # Shutdown DB client
        if self._db_client:
            await self._db_client.shutdown()

        logger.info("Disconnected successfully.")
