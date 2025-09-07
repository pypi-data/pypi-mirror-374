from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from programming_game import GameClient
    from programming_game.db import DBClient, DBSessionManager, Event, Intent

    HAS_DB = True
except ImportError:
    HAS_DB = False
    DBClient = None
    DBSessionManager = None
    Event = None
    Intent = None
    GameClient = None


@pytest.mark.skipif(not HAS_DB, reason="Database dependencies not installed")
class TestDBClient:
    @patch("programming_game.db.create_async_engine")
    def test_init_with_env_var(self, mock_engine, monkeypatch):
        """Test DBClient initialization with DATABASE_URL env var."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/test")
        client = DBClient()
        assert client.session_manager.database_url == "postgresql://user:pass@localhost/test"

    @patch("programming_game.db.create_async_engine")
    def test_init_with_explicit_url(self, mock_engine):
        """Test DBClient initialization with explicit database_url."""
        url = "postgresql://user:pass@localhost/test"
        client = DBClient(database_url=url)
        assert client.session_manager.database_url == url

    def test_init_no_url(self, monkeypatch):
        """Test DBClient initialization without DATABASE_URL."""
        monkeypatch.delenv("DATABASE_URL", raising=False)
        with pytest.raises(ValueError, match="DATABASE_URL environment variable not set"):
            DBClient()

    @patch("programming_game.db.create_async_engine")
    @pytest.mark.asyncio
    async def test_initialize(self, mock_engine):
        """Test DBClient initialization."""
        mock_conn = AsyncMock()
        mock_engine.begin.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.begin.return_value.__aexit__ = AsyncMock(return_value=None)

        client = DBClient(database_url="postgresql://test")
        client.session_manager.engine = mock_engine

        await client.initialize()

        assert client._initialized is True
        mock_conn.run_sync.assert_called_once()
        assert mock_conn.execute.call_count == 2  # Two hypertables created

    @patch("programming_game.db.create_async_engine")
    @pytest.mark.asyncio
    async def test_get_session(self, mock_engine):
        """Test getting a database session."""
        client = DBClient(database_url="postgresql://test")
        mock_session = AsyncMock()
        client.session_manager.get_session = AsyncMock(return_value=mock_session)

        session = await client.get_session()
        assert session == mock_session

    @patch("programming_game.db.create_async_engine")
    @pytest.mark.asyncio
    async def test_log_event(self, mock_engine):
        """Test logging an event."""
        client = DBClient(database_url="postgresql://test")
        client.event_queue.put = AsyncMock()

        await client.log_event(
            event_type="test_event",
            direction="in",
            data={"key": "value"},
            character_id="char1",
            instance_id="inst1",
            user_id="user1",
        )

        client.event_queue.put.assert_called_once()
        # Check that the event was created with correct data
        call_args = client.event_queue.put.call_args[0][0]
        assert isinstance(call_args.timestamp, datetime)
        assert call_args.event_type == "test_event"
        assert call_args.direction == "in"
        assert call_args.data == {"key": "value"}
        assert call_args.character_id == "char1"
        assert call_args.instance_id == "inst1"
        assert call_args.user_id == "user1"

    @patch("programming_game.db.create_async_engine")
    @pytest.mark.asyncio
    async def test_log_event_invalid_direction(self, mock_engine):
        """Test logging an event with invalid direction."""
        client = DBClient(database_url="postgresql://test")

        with pytest.raises(ValueError, match="Invalid direction for event: out"):
            await client.log_event(
                event_type="test_event",
                direction="out",
                data={"key": "value"},
            )

    @patch("programming_game.db.create_async_engine")
    @pytest.mark.asyncio
    async def test_log_intent(self, mock_engine):
        """Test logging an intent."""
        client = DBClient(database_url="postgresql://test")
        client.intent_queue.put = AsyncMock()

        await client.log_intent(
            intent_type="test_intent",
            data={"key": "value"},
            character_id="char1",
            instance_id="inst1",
            user_id="user1",
        )

        client.intent_queue.put.assert_called_once()
        # Check that the intent was created with correct data
        call_args = client.intent_queue.put.call_args[0][0]
        assert isinstance(call_args.timestamp, datetime)
        assert call_args.intent_type == "test_intent"
        assert call_args.data == {"key": "value"}
        assert call_args.character_id == "char1"
        assert call_args.instance_id == "inst1"
        assert call_args.user_id == "user1"

    @patch("programming_game.db.create_async_engine")
    @pytest.mark.asyncio
    async def test_queue_user_event(self, mock_engine):
        """Test queuing a user event."""
        client = DBClient(database_url="postgresql://test")
        client.log_event = AsyncMock()

        await client.queue_user_event({"custom": "data"}, user_id="user1")

        client.log_event.assert_called_once_with(
            "user_event",
            "user",
            {"custom": "data"},
            user_id="user1",
        )


@pytest.mark.skipif(not HAS_DB, reason="Database dependencies not installed")
class TestGameClientDBIntegration:
    @patch("programming_game.db.create_async_engine")
    def test_init_with_db_enabled(self, mock_engine):
        """Test GameClient initialization with DB enabled."""
        client = GameClient(
            credentials={"id": "test", "key": "key"}, enable_db=True, database_url="postgresql://test"
        )
        assert client._db_client is not None

    def test_init_with_db_disabled(self):
        """Test GameClient initialization with DB disabled."""
        client = GameClient(credentials={"id": "test", "key": "key"})
        assert client._db_client is None

    @patch("programming_game.db.create_async_engine")
    @pytest.mark.asyncio
    async def test_get_db_session_with_db(self, mock_engine):
        """Test get_db_session when DB is enabled."""
        client = GameClient(
            credentials={"id": "test", "key": "key"}, enable_db=True, database_url="postgresql://test"
        )
        mock_session = AsyncMock()
        client._db_client.get_session = AsyncMock(return_value=mock_session)

        session = await client.get_db_session()
        assert session == mock_session

    @pytest.mark.asyncio
    async def test_get_db_session_without_db(self):
        """Test get_db_session when DB is disabled."""
        client = GameClient(credentials={"id": "test", "key": "key"})

        with pytest.raises(RuntimeError, match="Database integration not enabled"):
            await client.get_db_session()

    @patch("programming_game.db.create_async_engine")
    @pytest.mark.asyncio
    async def test_queue_event_with_db(self, mock_engine):
        """Test queue_event when DB is enabled."""
        client = GameClient(
            credentials={"id": "test", "key": "key"}, enable_db=True, database_url="postgresql://test"
        )
        client._db_client.queue_user_event = AsyncMock()

        await client.queue_event({"event": "data"}, user_id="user1")

        client._db_client.queue_user_event.assert_called_once_with({"event": "data"}, "user1")

    @pytest.mark.asyncio
    async def test_queue_event_without_db(self, caplog):
        """Test queue_event when DB is disabled."""
        client = GameClient(credentials={"id": "test", "key": "key"})

        await client.queue_event({"event": "data"})

        assert "Database integration not enabled" in caplog.text


@pytest.mark.skipif(not HAS_DB, reason="Database dependencies not installed")
class TestEventModel:
    def test_event_creation(self):
        """Test Event model creation."""
        timestamp = datetime.now(timezone.utc)
        event = Event(
            timestamp=timestamp,
            event_type="test",
            direction="in",
            data={"key": "value"},
            character_id="char1",
            instance_id="inst1",
            user_id="user1",
        )

        assert event.timestamp == timestamp
        assert event.event_type == "test"
        assert event.direction == "in"
        assert event.data == {"key": "value"}
        assert event.character_id == "char1"
        assert event.instance_id == "inst1"
        assert event.user_id == "user1"


@pytest.mark.skipif(not HAS_DB, reason="Database dependencies not installed")
class TestIntentModel:
    def test_intent_creation(self):
        """Test Intent model creation."""
        timestamp = datetime.now(timezone.utc)
        intent = Intent(
            timestamp=timestamp,
            intent_type="test",
            data={"key": "value"},
            character_id="char1",
            instance_id="inst1",
            user_id="user1",
        )

        assert intent.timestamp == timestamp
        assert intent.intent_type == "test"
        assert intent.data == {"key": "value"}
        assert intent.character_id == "char1"
        assert intent.instance_id == "inst1"
        assert intent.user_id == "user1"
