OLLAMA_URL = "http://localhost:11434/api/chat"

PERMISSION_MODES = {
    "1": "Read + Write (Current Directory)",
    "2": "Ask Before Edit (Current Directory)",
    "3": "Read Only (Current Directory)",
    "4": "Ask Before Edit (Anywhere)",
    "5": "Read Only (Anywhere)",
    "6": "Full Read + Write (Anywhere) [DANGER]",
}

CURRENT_PERMISSION = "3"
DISPLAY_MODE = "standard"

ACTIVE_MODELS = {
    "planner": "qwen3:8b",
    "coder": "qwen2.5-coder:7b",
    "reviewer": "qwen3:8b",
    "classifier": "qwen3.5:0.8b",
}
