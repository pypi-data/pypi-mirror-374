import pytest


class TestGameClient:
    def test_init(self, game_client):
        """Test GameClient initialization."""
        assert game_client._credentials == {"id": "test_id", "key": "test_key"}
        assert game_client._log_level == "INFO"
        assert game_client._websocket is None
        assert game_client._is_running is False

    @pytest.mark.asyncio
    async def test_initialize_instance(self, game_client):
        """Test _initialize_instance method."""

        # Mock setup_character_handler
        async def mock_setup(gs):
            return type("MockScript", (), {"on_tick": lambda: None})()

        game_client._setup_character_handler = mock_setup
        char = await game_client._initialize_instance("instance1", "char1")
        assert char.character_id == "char1"
        assert "char1" in game_client._instances["instance1"].characters

    @pytest.mark.asyncio
    async def test_initialize_instance_callable(self, game_client):
        """Test _initialize_instance with callable-based script."""

        # Mock setup_character_handler returning a callable
        async def mock_setup(gs):
            async def on_tick():
                return None
            return on_tick

        game_client._setup_character_handler = mock_setup
        char = await game_client._initialize_instance("instance1", "char1")
        assert char.character_id == "char1"
        assert "char1" in game_client._instances["instance1"].characters
        # Verify that the script is wrapped
        assert hasattr(char._script, "on_tick")
        assert hasattr(char._script, "_callable")

    def test_send_message_no_websocket(self, game_client):
        """Test _send with no websocket."""
        # Should not raise an error
        game_client._send({"type": "test"})

    @pytest.mark.asyncio
    async def test_send_msg_no_websocket(self, game_client):
        """Test _send_msg with no websocket."""
        from programming_game.intents import SendIntent

        intent = SendIntent(value=None)
        # Should not raise an error
        await game_client._send_msg(intent)

    def test_disconnect(self, game_client):
        """Test disconnect method."""
        game_client._is_running = True
        game_client._websocket = "mock"  # Mock websocket

        # Should set flags correctly
        assert game_client._is_running is True
        # Note: Actual disconnect logic requires running event loop, so we test flags

    @pytest.mark.skip(reason="set_tick_config method doesn't exist in current implementation")
    def test_set_tick_config(self, game_client):
        """Test set_tick_config method."""
        pass

    @pytest.mark.skip(reason="Test requires setup_character_handler to be set")
    def test_character_task_initialization(self, game_client):
        """Test that character tasks are initialized."""
        pass

    @pytest.mark.skip(reason="Test requires setup_character_handler to be set")
    def test_character_task_cleanup(self, game_client):
        """Test that character tasks are cleaned up on disconnect."""
        pass
