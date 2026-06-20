from ai.ollama_client import OllamaClient
from core.config import ACTIVE_MODELS
from core.models import IntentCategories


class IntentClassifier:
    INTENTS = {
        IntentCategories.SYSTEM_COMMAND,
        IntentCategories.TOOL_ACTION,
        IntentCategories.FILE_OPERATION,
        IntentCategories.PROJECT_REVIEW,
        IntentCategories.PROJECT_QA,
        IntentCategories.CODE_CHANGE,
        IntentCategories.MULTI_STEP_TASK,
        IntentCategories.UNKNOWN,
    }

    @staticmethod
    def classify(prompt: str):
        classifier_prompt = f"""You are an intent classifier.

Return ONLY one intent from:
SYSTEM_COMMAND
TOOL_ACTION
FILE_OPERATION
PROJECT_REVIEW
PROJECT_QA
CODE_CHANGE
MULTI_STEP_TASK
UNKNOWN

Examples:
User: add login page
Intent: CODE_CHANGE

User: create tests
Intent: CODE_CHANGE

User: explain authentication
Intent: PROJECT_QA

User: review project
Intent: PROJECT_REVIEW

User: list files
Intent: TOOL_ACTION

User: open README.md
Intent: FILE_OPERATION

User: {prompt}
Intent:
"""
        try:
            result = OllamaClient.chat(ACTIVE_MODELS["classifier"], classifier_prompt)
        except Exception:
            return IntentCategories.UNKNOWN
        intent = result.strip().split()[0].upper()
        return intent if intent in IntentClassifier.INTENTS else IntentCategories.UNKNOWN
