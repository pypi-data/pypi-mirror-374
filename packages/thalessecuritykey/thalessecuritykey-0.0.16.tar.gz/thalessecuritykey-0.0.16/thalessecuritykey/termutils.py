import sys
from typing import Optional, Type, Union
from colorama import init, Fore, Style

_IS_COLORAMA_INITIALIZED = False

def _ensure_colorama_initialized():
    """Initialize Colorama only one time"""
    global _IS_COLORAMA_INITIALIZED
    if not _IS_COLORAMA_INITIALIZED:
        init()
        _IS_COLORAMA_INITIALIZED = True


def print_color(
    *messages,
    color: str = Fore.RESET,
    bright: bool = False,
    exception: Optional[Union[Exception, Type[Exception]]] = None,
    traceback: bool = False
) -> None:
    """
    Enhanced colored print with exception handling.
    
    Args:
        *messages: Text to print (auto-converted to str)
        color: Fore.COLOR constant (e.g., Fore.RED)
        bright: If True, uses bold text
        exception: Exception instance or type to display
        traceback: If True, prints full traceback (requires exception instance)
    """
    _ensure_colorama_initialized()
    style = Style.BRIGHT if bright else ""
    parts = [str(m) for m in messages]
    
    if exception:
        exc_type = type(exception) if isinstance(exception, Exception) else exception
        exc_msg = str(exception) if isinstance(exception, Exception) else ""
        
        parts.append(f"\n{exc_type.__name__}: {exc_msg}")
        
        if traceback and isinstance(exception, Exception):
            import traceback as tb
            parts.append(f"\n{tb.format_exc()}")

    text = " ".join(parts)
    print(f"{style}{color}{text}{Style.RESET_ALL}")

# Keep the existing input_color function from previous example
def input_color(prompt: str, color: str = Fore.YELLOW, bright: bool = False) -> str:
    """Colored input prompt (unchanged from previous implementation)"""
    _ensure_colorama_initialized()
    style = Style.BRIGHT if bright else ""
    sys.stdout.write(f"{style}{color}{prompt}{Style.RESET_ALL}")
    sys.stdout.flush()
    return input()

###############################################################################
# Shortcuts

def print_red(
        *messages,
        color: str = Fore.RESET,
        bright: bool = False,
        exception: Optional[Union[Exception, Type[Exception]]] = None,
        traceback: bool = False
    ) -> None:
    """Display a Red message."""
    return print_color(*messages, color=Fore.RED, bright=bright, exception=exception, traceback=traceback)