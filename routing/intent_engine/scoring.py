from routing.intent_engine.models import IntentMatch


class Scoring:
    @staticmethod
    def score_intent(normalized_text: str, intent_rule):
        matched = []
        score = 0
        tokens = set(normalized_text.split())

        for alias in intent_rule.aliases:
            if alias in normalized_text:
                matched.append(alias)
                score += 3

        for keyword in intent_rule.keywords:
            if keyword in tokens:
                matched.append(keyword)
                score += 1

        return IntentMatch(
            intent=intent_rule.intent,
            score=score,
            matched_keywords=tuple(matched),
        )

    @staticmethod
    def score_all(normalized_text: str, intent_rules):
        matches = [Scoring.score_intent(normalized_text, rule) for rule in intent_rules]
        scores = {match.intent: match.score for match in matches}
        return matches, scores
