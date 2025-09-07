import asyncio
import contextlib
import os
from asyncio import Queue
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, TIMESTAMP, String, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .logging import logger


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), primary_key=True
    )
    event_type: Mapped[str] = mapped_column(String(100))
    direction: Mapped[str] = mapped_column(String(10))  # 'in', 'user'
    data: Mapped[dict[str, Any]] = mapped_column(JSON)
    character_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    instance_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)


class Intent(Base):
    __tablename__ = "intents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), primary_key=True
    )
    intent_type: Mapped[str] = mapped_column(String(100))
    data: Mapped[dict[str, Any]] = mapped_column(JSON)
    character_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    instance_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)


class DBSessionManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_async_engine(database_url, echo=False)
        self.session_maker = async_sessionmaker(self.engine, expire_on_commit=False)

    async def init_db(self) -> None:
        """Initialize database and create tables with TimescaleDB hypertables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            # Create hypertables for events and intents tables
            await conn.execute(
                text("SELECT create_hypertable('events', 'timestamp', if_not_exists => TRUE);")
            )
            await conn.execute(
                text("SELECT create_hypertable('intents', 'timestamp', if_not_exists => TRUE);")
            )
        logger.info("Database initialized with TimescaleDB hypertables")

    async def get_session(self) -> AsyncSession:
        """Get a new async session."""
        return self.session_maker()

    async def close(self) -> None:
        """Close the database engine."""
        await self.engine.dispose()


class DBClient:
    def __init__(self, database_url: str | None = None):
        if database_url is None:
            database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")

        self.session_manager = DBSessionManager(database_url)
        self.event_queue: Queue[Event] = Queue()
        self.intent_queue: Queue[Intent] = Queue()
        self.batch_task: asyncio.Task[Any] | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the database and start batch processing."""
        if not self._initialized:
            await self.session_manager.init_db()
            self.batch_task = asyncio.create_task(self._batch_insert_loop())
            self._initialized = True
            logger.info("DBClient initialized and batch processing started")

    async def get_session(self) -> AsyncSession:
        """Get a database session for user operations."""
        return await self.session_manager.get_session()

    async def log_event(
        self,
        event_type: str,
        direction: str,
        data: dict[str, Any],
        character_id: str | None = None,
        instance_id: str | None = None,
        user_id: str | None = None,
    ):
        """Log an incoming event to the queue for batch processing."""
        if direction not in ["in", "user"]:
            raise ValueError(f"Invalid direction for event: {direction}. Must be 'in' or 'user'")
        event = Event(
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            direction=direction,
            data=data,
            character_id=character_id,
            instance_id=instance_id,
            user_id=user_id,
        )
        await self.event_queue.put(event)

    async def log_intent(
        self,
        intent_type: str,
        data: dict[str, Any],
        character_id: str | None = None,
        instance_id: str | None = None,
        user_id: str | None = None,
    ):
        """Log an outgoing intent to the queue for batch processing."""
        intent = Intent(
            timestamp=datetime.now(timezone.utc),
            intent_type=intent_type,
            data=data,
            character_id=character_id,
            instance_id=instance_id,
            user_id=user_id,
        )
        await self.intent_queue.put(intent)

    async def queue_user_event(self, event_data: dict[str, Any], user_id: str | None = None):
        """Queue a user-defined event for logging."""
        await self.log_event("user_event", "user", event_data, user_id=user_id)

    async def _batch_insert_loop(self) -> None:
        """Background task to process event and intent queues in batches."""
        while True:
            try:
                events = []
                intents = []

                # Collect all available events
                while not self.event_queue.empty():
                    events.append(self.event_queue.get_nowait())

                # Collect all available intents
                while not self.intent_queue.empty():
                    intents.append(self.intent_queue.get_nowait())

                # Insert events
                if events:
                    async with await self.session_manager.get_session() as session:
                        session.add_all(events)
                        await session.commit()
                    # logger.debug(f"Inserted {len(events)} events into database")

                # Insert intents
                if intents:
                    async with await self.session_manager.get_session() as session:
                        session.add_all(intents)
                        await session.commit()
                    # logger.debug(f"Inserted {len(intents)} intents into database")

                await asyncio.sleep(0.5)  # 2 times per second
            except Exception as e:
                logger.error(f"Error in batch insert loop: {e}", exc_info=True)
                await asyncio.sleep(1)  # Wait a bit longer on error

    async def shutdown(self) -> None:
        """Shutdown the DB client and cleanup resources."""
        if self.batch_task:
            self.batch_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.batch_task
        await self.session_manager.close()
        logger.info("DBClient shutdown complete")
