class IntentCategories:
    SYSTEM_COMMAND = "SYSTEM_COMMAND"
    TOOL_ACTION = "TOOL_ACTION"
    FILE_OPERATION = "FILE_OPERATION"
    REPO_LIST = "REPO_LIST"
    REPO_TREE = "REPO_TREE"
    REPO_FIND = "REPO_FIND"
    REPO_SUMMARY = "REPO_SUMMARY"
    FILE_READ = "FILE_READ"
    SEARCH_TEXT = "SEARCH_TEXT"
    PROJECT_REVIEW = "PROJECT_REVIEW"
    PROJECT_QA = "PROJECT_QA"
    CODE_CHANGE = "CODE_CHANGE"
    MULTI_STEP_TASK = "MULTI_STEP_TASK"
    UNKNOWN = "UNKNOWN"


class CommandStatus:
    HANDLED = "HANDLED"
    EXIT = "EXIT"
    NOT_HANDLED = "NOT_HANDLED"


class RuntimeContext:
    def __init__(self, console, current_permission, display_mode, base_dir):
        self.console = console
        self.current_permission = current_permission
        self.display_mode = display_mode
        self.base_dir = base_dir
