from programming_game import GameState
from programming_game.schema.events import (
    AcceptedQuestEvent,
    AnyEvent,
    ArenaEvent,
    InventoryEvent,
    QuestAbandonedEvent,
    QuestCompletedEvent,
    QuestFailedEvent,
    QuestProgressEvent,
    QuestStartedEvent,
    QuestUpdateEvent,
)
from programming_game.schema.instance_character import InstanceCharacter
from programming_game.schema.other import PlayerStats
from programming_game.schema.units import Player


class TestArenaEvent:
    def test_arena_event(self):
        """Test ArenaEvent creation."""
        event = ArenaEvent(duration=300)
        assert event.duration == 300

    def test_any_event_includes_arena_event(self):
        """Test that AnyEvent union includes ArenaEvent."""
        arena_event: AnyEvent = ArenaEvent(duration=600)
        assert isinstance(arena_event, AnyEvent)


class TestQuestEvents:
    def test_accepted_quest_event(self):
        """Test AcceptedQuestEvent creation."""
        from programming_game.schema.other import Position, Quest, QuestStep

        quest = Quest(
            id="test_quest",
            name="Test Quest",
            start_npc="test_start",
            end_npc="test_end",
            steps=[
                QuestStep(
                    type="turn_in",
                    target="test_target",
                    requiredItems={"item": 1},
                    position=Position(x=1, y=1),
                )
            ],
        )
        event = AcceptedQuestEvent(unitId="test_unit", quest=quest)
        assert event.unitId == "test_unit"
        assert event.quest.id == "test_quest"
        assert event.quest.name == "Test Quest"

    def test_quest_started_event(self):
        """Test QuestStartedEvent creation."""
        event = QuestStartedEvent(quest="test_quest", npc="test_npc")
        assert event.quest == "test_quest"
        assert event.npc == "test_npc"

    def test_quest_completed_event(self):
        """Test QuestCompletedEvent creation."""
        rewards = {"gold": 100, "xp": 50}
        event = QuestCompletedEvent(quest="test_quest", npc="test_npc", rewards=rewards)
        assert event.quest == "test_quest"
        assert event.npc == "test_npc"
        assert event.rewards == rewards

    def test_quest_progress_event(self):
        """Test QuestProgressEvent creation."""
        event = QuestProgressEvent(quest="test_quest", objective="kill_goblins", current=5, target=10)
        assert event.quest == "test_quest"
        assert event.objective == "kill_goblins"
        assert event.current == 5
        assert event.target == 10

    def test_quest_failed_event(self):
        """Test QuestFailedEvent creation."""
        event = QuestFailedEvent(quest="test_quest", reason="timeout")
        assert event.quest == "test_quest"
        assert event.reason == "timeout"

    def test_quest_abandoned_event(self):
        """Test QuestAbandonedEvent creation."""
        event = QuestAbandonedEvent(quest="test_quest")
        assert event.quest == "test_quest"

    def test_quest_update_event(self):
        """Test QuestUpdateEvent creation."""
        quest_data = {"id": "test_quest", "name": "Test Quest", "steps": []}
        event = QuestUpdateEvent(unitId="test_unit", quest=quest_data)
        assert event.unitId == "test_unit"
        assert event.quest == quest_data

    def test_any_event_includes_quest_events(self):
        """Test that AnyEvent union includes all quest events."""
        from programming_game.schema.other import Position, Quest, QuestStep

        quest = Quest(
            id="test_quest",
            name="Test Quest",
            start_npc="test_start",
            end_npc="test_end",
            steps=[
                QuestStep(
                    type="turn_in",
                    target="test_target",
                    requiredItems={"item": 1},
                    position=Position(x=1, y=1),
                )
            ],
        )

        # Test that quest events can be assigned to AnyEvent
        accepted_quest: AnyEvent = AcceptedQuestEvent(unitId="test_unit", quest=quest)
        quest_started: AnyEvent = QuestStartedEvent(quest="test", npc="npc")
        quest_completed: AnyEvent = QuestCompletedEvent(quest="test", npc="npc", rewards={})
        quest_progress: AnyEvent = QuestProgressEvent(quest="test", objective="obj", current=1, target=2)
        quest_failed: AnyEvent = QuestFailedEvent(quest="test", reason="failed")
        quest_abandoned: AnyEvent = QuestAbandonedEvent(quest="test")
        quest_update: AnyEvent = QuestUpdateEvent(unitId="test_unit", quest={"id": "test"})

        assert isinstance(accept_quest, AnyEvent)
        assert isinstance(accepted_quest, AnyEvent)
        assert isinstance(quest_started, AnyEvent)
        assert isinstance(quest_completed, AnyEvent)
        assert isinstance(quest_progress, AnyEvent)
        assert isinstance(quest_failed, AnyEvent)
        assert isinstance(quest_abandoned, AnyEvent)
        assert isinstance(quest_update, AnyEvent)

    def test_quest_event_handlers(self):
        """Test that InstanceCharacter has quest event handlers."""
        # Create a minimal GameState and InstanceCharacter for testing
        from programming_game.schema.other import Position, UnitTrades

        player = Player(
            unitsInSight={},
            calories=1000,
            id="test_player",
            name="Test Player",
            hp=100,
            tp=0,
            mp=100,
            position=Position(x=0, y=0),
            lastUpdate=0,
            intent=None,
            inventory={},
            npc=False,
            race="human",
            trades=UnitTrades(),
            bounty=0,
            role="warrior",
            stats=PlayerStats(
                maxHp=100,
                maxMp=100,
                maxTp=100,
                mpRegen=1.0,
                attack=10,
                defense=5,
                movementSpeed=1.0,
                radius=0.5,
            ),
        )

        game_state = GameState(
            character_id="test_player", instance_id="test_instance", units={"test_player": player}
        )

        # Create InstanceCharacter
        char = InstanceCharacter(_script=None, character_id="test_char", game_state=game_state, instance=None)

        # Test that handlers exist and can be called without errors
        quest_started = QuestStartedEvent(quest="test_quest", npc="test_npc")
        quest_completed = QuestCompletedEvent(quest="test_quest", npc="test_npc", rewards={"gold": 100})
        quest_progress = QuestProgressEvent(quest="test_quest", objective="kill", current=1, target=5)
        quest_failed = QuestFailedEvent(quest="test_quest", reason="timeout")
        quest_abandoned = QuestAbandonedEvent(quest="test_quest")
        quest_update = QuestUpdateEvent(unitId="test_unit", quest={"id": "test_quest"})

        # These should not raise exceptions
        from programming_game.schema.other import Position, Quest, QuestStep

        quest_obj = Quest(
            id="test_quest",
            name="Test Quest",
            start_npc="test_start",
            end_npc="test_end",
            steps=[
                QuestStep(
                    type="turn_in",
                    target="test_target",
                    requiredItems={"item": 1},
                    position=Position(x=1, y=1),
                )
            ],
        )

        accepted_quest = AcceptedQuestEvent(unitId="test_unit", quest=quest_obj)

        char.handle_accepted_quest_event(accepted_quest)
        char.handle_quest_started_event(quest_started)
        char.handle_quest_completed_event(quest_completed)
        char.handle_quest_progress_event(quest_progress)
        char.handle_quest_failed_event(quest_failed)
        char.handle_quest_abandoned_event(quest_abandoned)
        char.handle_quest_update_event(quest_update)


class TestInventoryEvent:
    def test_inventory_event(self):
        """Test InventoryEvent creation."""
        inventory = {"sword": 1, "shield": 2, "potion": 0}
        event = InventoryEvent(unitId="test_unit", inventory=inventory)
        assert event.unitId == "test_unit"
        assert event.inventory == inventory

    def test_any_event_includes_inventory_event(self):
        """Test that AnyEvent union includes InventoryEvent."""
        inventory_event: AnyEvent = InventoryEvent(unitId="test_unit", inventory={"item": 5})
        assert isinstance(inventory_event, AnyEvent)

    def test_inventory_event_handler(self):
        """Test that InstanceCharacter has inventory event handler."""
        from programming_game.schema.other import Position, UnitTrades

        player = Player(
            unitsInSight={},
            calories=1000,
            id="test_player",
            name="Test Player",
            hp=100,
            tp=0,
            mp=100,
            position=Position(x=0, y=0),
            lastUpdate=0,
            intent=None,
            inventory={"sword": 1, "shield": 1},
            npc=False,
            race="human",
            trades=UnitTrades(),
            bounty=0,
            role="warrior",
            stats=PlayerStats(
                maxHp=100,
                maxMp=100,
                maxTp=100,
                mpRegen=1.0,
                attack=10,
                defense=5,
                movementSpeed=1.0,
                radius=0.5,
            ),
        )

        game_state = GameState(
            character_id="test_player", instance_id="test_instance", units={"test_player": player}
        )

        # Create InstanceCharacter
        char = InstanceCharacter(
            _script=None,
            character_id="test_player",
            game_state=game_state,
            instance=None,
            units={"test_player": player},
        )

        # Test inventory update
        inventory_event = InventoryEvent(
            unitId="test_player", inventory={"sword": 2, "shield": 0, "potion": 3}
        )
        char.handle_inventory_event(inventory_event)

        # Check that inventory was updated correctly
        assert player.inventory["sword"] == 2
        assert "shield" not in player.inventory  # Should be removed due to 0 amount
        assert player.inventory["potion"] == 3
