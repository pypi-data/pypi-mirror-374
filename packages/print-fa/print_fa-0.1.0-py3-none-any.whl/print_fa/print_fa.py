
import arabic_reshaper
from bidi.algorithm import get_display

class Colors:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_fa(text, color=None, bold=False, underline=False):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)

    formatted_text = bidi_text

    if bold:
        formatted_text = Colors.BOLD + formatted_text
    if underline:
        formatted_text = Colors.UNDERLINE + formatted_text
    if color:
        if hasattr(Colors, color.upper()):
            formatted_text = getattr(Colors, color.upper()) + formatted_text
        else:
            print(f"Warning: Invalid color '{color}'. Using default color.")

    print(formatted_text + Colors.RESET)


