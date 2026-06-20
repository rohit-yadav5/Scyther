from core.models import IntentCategories
from routing.intent_engine.entity_extractor import EntityExtractor
from routing.intent_engine.normalizer import Normalizer
from routing.intent_engine.rules import INTENT_RULES
from routing.intent_engine.scoring import Scoring
from routing.intent_engine.models import IntentResult


class IntentMatcher:
    @staticmethod
    def match(user_input: str):
        normalized = Normalizer.normalize(user_input)
        matches, scores = Scoring.score_all(normalized, INTENT_RULES)
        extracted_entities = EntityExtractor.extract(user_input)

        best_match = max(matches, key=lambda match: (match.score, len(match.matched_keywords)), default=None)
        if best_match is None or best_match.score == 0:
            return IntentResult(
                intent=IntentCategories.UNKNOWN,
                score=0,
                matched_keywords=(),
                extracted_entities=extracted_entities,
                scores=scores,
            )

        return IntentResult(
            intent=best_match.intent,
            score=best_match.score,
            matched_keywords=best_match.matched_keywords,
            extracted_entities=extracted_entities,
            scores=scores,
        )
