"""Preview Module - Routes to Interactive TUI"""
from redaction_system.cli.interactive_preview import show_interactive_preview

def show_preview(filepath, prompt, orchestrator):
    """
    Show preview of entities to be redacted
    
    Returns:
        bool: True if user approves, False if cancelled
    """
    return show_interactive_preview(filepath, prompt, orchestrator)
