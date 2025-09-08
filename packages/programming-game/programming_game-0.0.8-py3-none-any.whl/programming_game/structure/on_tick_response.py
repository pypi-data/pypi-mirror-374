
from programming_game.schema.intents import AnyIntent


class OnTickResponseType:
    """
    Base class for all types of responses that can be returned from on_tick.
    You can use this class to implement your own custom responses to use within your bot.
    The Library will assume a "None" response.
    """
    pass

class TickPause(OnTickResponseType):
    def __init__(self, time: int | float):
        self.time = time

class PreDelayedIntent(OnTickResponseType):
    """
    DelayedIntent is used to delay the execution of an intent.
    Note: The bot will not execute any ticks until the intent is executed.
    """
    def __init__(self, intent: AnyIntent, time: int | float):
        self.intent = intent
        self.time = time

class PostDelayedIntent(OnTickResponseType):
    """
    There will be a delay added after the intent is executed.
    Note: No tick will be executed until time is over.
    """
    def __init__(self, intent: AnyIntent, time: int | float):
        self.intent = intent
        self.time = time

    def __repr__(self):
        return f"PostDelayedIntent(intent={self.intent}, time={self.time})"


OnTickResponse = AnyIntent | OnTickResponseType | None
