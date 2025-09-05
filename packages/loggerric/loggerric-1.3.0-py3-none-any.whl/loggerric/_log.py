from colorama import Fore
from loggerric._log_levels import *
from loggerric._timestamp import *

def _apply_highlight(text:str, highlight:str, color:str, hl_color:str=Fore.YELLOW):
    highlighted_text = text

    if isinstance(highlight, str):
        highlighted_text = highlighted_text.replace(highlight, hl_color + highlight + color)
    elif isinstance(highlight, list):
        for hl in highlight:
            highlighted_text = highlighted_text.replace(hl, hl_color + hl + color)

    return highlighted_text

class Log:
    """
    **Contains various logging methods.**
    """
    # Keep track of what should be logged
    _active_levels = { LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR, LogLevel.DEBUG }

    @classmethod
    def info(cls, *content:str, highlight:str|list[str]=None) -> None:
        """
        **Format a message as information.**

        *Parameters*:
        - `*content` (str): The content you want printed.
        - `highlight` (str|list[str]): Text that should be highlighted when printing. (Case Sensitive)

        *Example*:
        ```python
        Log.info('Hello World!', ..., highlight='World')
        ```
        """
        # Log the content
        if LogLevel.INFO in cls._active_levels:
            raw_text = " ".join([str(c) for c in content])

            # Highlight text
            highlighted_text = _apply_highlight(raw_text, highlight, Fore.GREEN)

            print(f'{Timestamp.get(internal_call=True)}{Fore.GREEN}[i] {highlighted_text}{Fore.WHITE}')

    @classmethod
    def warn(cls, *content:str, highlight:str|list[str]=None) -> None:
        """
        **Format a message as a warning.**

        *Parameters*:
        - `*content` (str): The content you want printed.
        - `highlight` (str|list[str]): Text that should be highlighted when printing. (Case Sensitive)

        *Example*:
        ```python
        Log.warn('Hello World!', ..., highlight='World')
        ```
        """
        # Log the content
        if LogLevel.WARN in cls._active_levels:
            raw_text = " ".join([str(c) for c in content])

            # Highlight text
            highlighted_text = _apply_highlight(raw_text, highlight, Fore.YELLOW, Fore.WHITE)

            print(f'{Timestamp.get(internal_call=True)}{Fore.YELLOW}[w] {highlighted_text}{Fore.WHITE}')

    @classmethod
    def error(cls, *content:str, quit_after_log:bool=False, highlight:str|list[str]=None) -> None:
        """
        **Format a message as an error.**

        *Parameters*:
        - `*content` (str): The content you want printed.
        - `quit_after_log` (bool): Quit after logging the error.
        - `highlight` (str|list[str]): Text that should be highlighted when printing. (Case Sensitive)

        *Example*:
        ```python
        Log.error('Hello World!', ..., quit_after_log=True, highlight='World')
        ```
        """
        # Log the content
        if LogLevel.ERROR in cls._active_levels:
            raw_text = " ".join([str(c) for c in content])

            # Highlight text
            highlighted_text = _apply_highlight(raw_text, highlight, Fore.RED)

            print(f'{Timestamp.get(internal_call=True)}{Fore.RED}[!] {highlighted_text}{Fore.WHITE}')

            if quit_after_log: exit()

    @classmethod
    def debug(cls, *content:str, highlight:str|list[str]=None) -> None:
        """
        **Format a message as a debug message.**

        *Parameters*:
        - `*content` (str): The content you want printed.
        - `highlight` (str|list[str]): Text that should be highlighted when printing. (Case Sensitive)

        *Example*:
        ```python
        Log.debug('Hello World!', ..., highlight='World')
        ```
        """
        # Log the content
        if LogLevel.DEBUG in cls._active_levels:
            raw_text = " ".join([str(c) for c in content])

            # Highlight text
            highlighted_text = _apply_highlight(raw_text, highlight, Fore.LIGHTBLACK_EX)

            print(f'{Timestamp.get(internal_call=True)}{Fore.LIGHTBLACK_EX}[?] {highlighted_text}{Fore.WHITE}')
    
    @classmethod
    def enable(cls, *levels:LogLevel) -> None:
        """
        **Enable logging methods.**

        *Parameters*:
        - `*levels` (LogLevel): Levels that should be enabled.

        *Example*:
        ```python
        Log.enable(LogLevel.INFO, LogLevel.WARN, ...)
        ```
        """
        cls._active_levels.update(levels)
    
    @classmethod
    def disable(cls, *levels:LogLevel) -> None:
        """
        **Disable logging methods.**

        *Parameters*:
        - `*levels` (LogLevel): Levels that should be disabled.

        *Example*:
        ```python
        Log.disable(LogLevel.INFO, LogLevel.WARN, ...)
        ```
        """
        cls._active_levels.difference_update(levels)
    
    @classmethod
    def pretty_print(cls, data, indent:int=4, depth_level:int=0, inline:bool=False) -> None:
        """
        **Print any variable so they are more readable.**

        Intended use is for dictionaries and arrays, other variables still work.

        *Parameters*:
        - `data` (any): The data you want to pretty print.
        - `indent` (int): The indentation amount for the data.
        - `depth_level` (int): USED INTERNALLY, control what child depth the recursive call is at.
        - `inline` (bool): USED INTERNALLY, keeps track of key/value printing, as to not hop to next line.

        *Example*:
        ```python
        data = {
            'name': 'John Doe',
            'age': 27,
            'skills': ['this', 'and', 'that'],
            'status': None,
            'subdict': { 'source': True, 'the_list': ['English', 'Danish'] }
        }
        Log.pretty_print(data)
        ```
        """
        spacing = ' ' * (indent * depth_level)

        if depth_level == 0:
            print(Timestamp.get(internal_call=True))

        # Dictionary
        if isinstance(data, dict):
            if not inline:
                print(spacing + Fore.CYAN + '{')
            else:
                print(Fore.CYAN + '{')
            for key, value in data.items():
                key_spacing = ' ' * (indent * (depth_level + 1))
                print(key_spacing + Fore.YELLOW + str(key) + Fore.WHITE + ': ', end="")
                if isinstance(value, (dict, list)):
                    cls.pretty_print(value, indent, depth_level + 1, inline=True)
                else:
                    cls.pretty_print(value, indent, depth_level + 1, inline=True)
            print(spacing + Fore.CYAN + '}')

        # List
        elif isinstance(data, list):
            if not inline:
                print(spacing + Fore.MAGENTA + '[')
            else:
                print(Fore.MAGENTA + '[')
            for item in data:
                cls.pretty_print(item, indent, depth_level + 1, inline=False)
            print(spacing + Fore.MAGENTA + ']')

        # String
        elif isinstance(data, str):
            print((spacing if not inline else "") + Fore.GREEN + f'"{data}"')

        # Number
        elif isinstance(data, (int, float, complex)):
            print((spacing if not inline else "") + Fore.BLUE + str(data))

        # Boolean
        elif isinstance(data, bool):
            print((spacing if not inline else "") + Fore.LIGHTBLUE_EX + str(data))

        # None
        elif data is None:
            print((spacing if not inline else "") + Fore.RED + 'None')

        # Other
        else:
            print((spacing if not inline else "") + Fore.WHITE + str(data))