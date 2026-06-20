from routing.intent_engine.intent_matcher import IntentMatcher


class IntentRouter:
    @staticmethod
    def route(user_input: str):
        result = IntentMatcher.match(user_input)
        return result.intent

    @staticmethod
    def inspect(user_input: str):
        return IntentMatcher.match(user_input)
