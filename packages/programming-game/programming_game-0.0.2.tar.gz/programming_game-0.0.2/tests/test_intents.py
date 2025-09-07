from programming_game.intents import (
    AbandonQuestIntent,
    AcceptQuestIntent,
    AttackIntent,
    BaseIntent,
    EatIntent,
    MoveIntent,
    RespawnIntent,
    SendIntent,
    SendIntentValue,
)


class TestIntents:
    def test_base_intent_creation(self):
        """Test BaseIntent creation."""
        intent = BaseIntent()
        assert intent is not None

    def test_attack_intent(self):
        """Test AttackIntent."""
        intent = AttackIntent(target="enemy1")
        assert intent.target == "enemy1"

    def test_eat_intent(self):
        """Test EatIntent."""
        intent = EatIntent(item="apple", save=50)
        assert intent.item == "apple"
        assert intent.save == 50

    def test_move_intent(self):
        """Test MoveIntent."""
        from programming_game.schema.other import Position

        pos = Position(10, 20)
        intent = MoveIntent(position=pos)
        assert intent.position.x == 10
        assert intent.position.y == 20

    def test_respawn_intent(self):
        """Test RespawnIntent."""
        intent = RespawnIntent()
        assert intent is not None

    def test_abandon_quest_intent(self):
        """Test AbandonQuestIntent."""
        intent = AbandonQuestIntent(quest="quest1")
        assert intent.quest == "quest1"

    def test_accept_quest_intent(self):
        """Test AcceptQuestIntent."""
        intent = AcceptQuestIntent(questId="quest1", npcId="npc1")
        assert intent.questId == "quest1"
        assert intent.npcId == "npc1"

    def test_send_intent(self):
        """Test SendIntent."""
        value = SendIntentValue(c="char1", i="instance1", unitId="unit1", intent=None)
        intent = SendIntent(value=value)
        assert intent.value.c == "char1"
        assert intent.value.i == "instance1"
        assert intent.value.unitId == "unit1"
