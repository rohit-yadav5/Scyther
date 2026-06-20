import re

from core.models import IntentCategories


class IntentRouter:
    SYSTEM_COMMAND_PATTERNS = {"/help", "/model", "/display", "/permission", "/exit", "/bye"}
    TOOL_ACTION_PATTERNS = {"list files", "show files", "show directory", "pwd", "current directory"}
    FILE_OPERATION_PATTERNS = {r"^open\s+.+", r"^read\s+.+", r"^show file\s+.+",}
    PROJECT_REVIEW_PATTERNS = {"review project", "security review", "performance review", "audit codebase"}
    MULTI_STEP_TASK_PATTERNS = {"find bugs and fix them", "find all bugs and fix them", "review and fix", "fix all problems", "update readme", "generate report"}
    CODE_CHANGE_PATTERNS = {r"^(add|create|build|implement|fix|update|refactor|remove|replace|change|edit)\b", r"\b(login page|auth page|dashboard|api|endpoint|component|test|tests|feature)\b"}

    @staticmethod
    def route(user_input: str):
        text = user_input.lower().strip()

        if text in IntentRouter.SYSTEM_COMMAND_PATTERNS:
            return IntentCategories.SYSTEM_COMMAND
        if any(pattern in text for pattern in IntentRouter.TOOL_ACTION_PATTERNS):
            return IntentCategories.TOOL_ACTION
        if any(re.search(pattern, text) for pattern in IntentRouter.FILE_OPERATION_PATTERNS):
            return IntentCategories.FILE_OPERATION
        if any(pattern in text for pattern in IntentRouter.PROJECT_REVIEW_PATTERNS):
            return IntentCategories.PROJECT_REVIEW
        if any(pattern in text for pattern in IntentRouter.MULTI_STEP_TASK_PATTERNS):
            return IntentCategories.MULTI_STEP_TASK
        if any(re.search(pattern, text) for pattern in IntentRouter.CODE_CHANGE_PATTERNS):
            return IntentCategories.CODE_CHANGE
        return IntentCategories.UNKNOWN
