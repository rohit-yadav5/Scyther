from routing.command_router import _REGISTRY
from core.command_registry import COMMANDS


def test_command_registry_completeness():
    """Verify that every route defined in CommandRouter (except the alias /bye) exists in the registry."""
    for cmd in _REGISTRY:
        if cmd == "/bye":
            continue
        assert cmd in COMMANDS, f"Command {cmd} from CommandRouter._REGISTRY is missing from core/command_registry.py"


def test_command_registry_metadata_schema():
    """Verify that all commands in the registry have correct keys and types."""
    valid_categories = {"Repository", "Modification", "Git", "Release", "System"}
    
    for cmd_name, info in COMMANDS.items():
        assert isinstance(info, dict), f"{cmd_name} metadata must be a dictionary"
        
        # Check description
        assert "description" in info, f"{cmd_name} metadata must have a 'description'"
        assert isinstance(info["description"], str), f"{cmd_name} description must be a string"
        
        # Check usage
        assert "usage" in info, f"{cmd_name} metadata must have a 'usage'"
        assert isinstance(info["usage"], str), f"{cmd_name} usage must be a string"
        assert info["usage"].startswith(cmd_name), f"{cmd_name} usage must start with the command name"
        
        # Check category
        assert "category" in info, f"{cmd_name} metadata must have a 'category'"
        assert info["category"] in valid_categories, f"{cmd_name} category '{info['category']}' is invalid"
        
        # Check dangerous flag
        assert "dangerous" in info, f"{cmd_name} metadata must have a 'dangerous' flag"
        assert isinstance(info["dangerous"], bool), f"{cmd_name} dangerous flag must be a boolean"
        
        # Check requires_write flag
        assert "requires_write" in info, f"{cmd_name} metadata must have a 'requires_write' flag"
        assert isinstance(info["requires_write"], bool), f"{cmd_name} requires_write flag must be a boolean"
