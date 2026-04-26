# utils/prompts.py
from pathlib import Path


def prompt_for_title(current_title: str) -> str | None:
    """Prompt user for a new movie title when TMDB search fails."""
    response = input(f"Enter new title (or press Enter to skip): ").strip()
    if not response:
        return None
    return response


def prompt_keep_no_rename(prompt_text: str, default: str = "yes") -> str | None:
    """
    Prompt user with Keep, No, Rename options.
    
    Args:
        prompt_text: The question to display (e.g., "Keep The Matrix (1999)?")
        default: Default choice if user just presses Enter ("yes", "no", or "rename")
    
    Returns:
        "yes" to keep, "no" to reject, "rename" to rename, or None to cancel/skip
    """
    options = "Yes, No, Rename"
    if default == "yes":
        options = "Yes, No, Rename"
    elif default == "no":
        options = "yes, NO, rename"
    elif default == "rename":
        options = "yes, no, RENAME"
    
    while True:
        response = input(f"{prompt_text}? ({options}): ").strip().lower()
        
        if not response:
            return default
        
        if response in ("y", "yes"):
            return "yes"
        elif response in ("n", "no"):
            return "no"
        elif response in ("r", "rename"):
            return "rename"
        else:
            print(f"Invalid choice. Please enter yes, no, or rename.")