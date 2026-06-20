from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class IntentRule:
    intent: str
    keywords: tuple[str, ...]
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class IntentMatch:
    intent: str
    score: int
    matched_keywords: tuple[str, ...] = ()
    extracted_entities: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class IntentResult:
    intent: str
    score: int
    matched_keywords: tuple[str, ...]
    extracted_entities: dict[str, Any]
    scores: dict[str, int] = field(default_factory=dict)
