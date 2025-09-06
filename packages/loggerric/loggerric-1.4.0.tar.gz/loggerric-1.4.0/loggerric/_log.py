from colorama import Fore
from loggerric._timestamp import *
from loggerric._log_to_file import *
from enum import Enum, auto
import json

def _apply_highlight(text:str, highlight:str, color:str, hl_color:str=Fore.YELLOW):
    highlighted_text = text

    if isinstance(highlight, str):
        highlighted_text = highlighted_text.replace(highlight, hl_color + highlight + color)
    elif isinstance(highlight, list):
        for hl in highlight:
            highlighted_text = highlighted_text.replace(hl, hl_color + hl + color)

    return highlighted_text

class LogLevel(Enum):
    """
    **Enums used for logging.**
    """
    INFO = auto()
    WARN = auto()
    ERROR = auto()
    DEBUG = auto()

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
            raw_text = ' '.join([str(c) for c in content])

            # Highlight text
            highlighted_text = _apply_highlight(raw_text, highlight, Fore.GREEN)

            finished_text = f'{Timestamp.get(internal_call=True)}{Fore.GREEN}[i] {highlighted_text}{Fore.RESET}'
            print(finished_text)

            # Log to file
            if LogToFileLevel.INFO in LogToFile._active_levels:
                LogToFile._log(escape_ansi(finished_text))

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
            raw_text = ' '.join([str(c) for c in content])

            # Highlight text
            highlighted_text = _apply_highlight(raw_text, highlight, Fore.YELLOW, Fore.WHITE)

            finished_text = f'{Timestamp.get(internal_call=True)}{Fore.YELLOW}[w] {highlighted_text}{Fore.RESET}'
            print(finished_text)

            # Log to file
            if LogToFileLevel.WARN in LogToFile._active_levels:
                LogToFile._log(escape_ansi(finished_text))

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
            raw_text = ' '.join([str(c) for c in content])

            # Highlight text
            highlighted_text = _apply_highlight(raw_text, highlight, Fore.RED)

            finished_text = f'{Timestamp.get(internal_call=True)}{Fore.RED}[!] {highlighted_text}{Fore.RESET}'
            print(finished_text)

            # Log to file
            if LogToFileLevel.ERROR in LogToFile._active_levels:
                LogToFile._log(escape_ansi(finished_text))

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
            raw_text = ' '.join([str(c) for c in content])

            # Highlight text
            highlighted_text = _apply_highlight(raw_text, highlight, Fore.LIGHTBLACK_EX)

            finished_text = f'{Timestamp.get(internal_call=True)}{Fore.LIGHTBLACK_EX}[?] {highlighted_text}{Fore.RESET}'
            print(finished_text)

            # Log to file
            if LogToFileLevel.DEBUG in LogToFile._active_levels:
                LogToFile._log(escape_ansi(finished_text))
    
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
            timestamp = Timestamp.get(internal_call=True)
            print(timestamp)
            if LogToFileLevel.PRETTY_PRINT in LogToFile._active_levels:
                LogToFile._log(escape_ansi(timestamp))

        prefix_spacing = (spacing if not inline else '')

        # Dictionary
        if isinstance(data, dict):
            if not inline:
                print(spacing + Fore.CYAN + '{')
            else:
                print(Fore.CYAN + '{')
            for key, value in data.items():
                key_spacing = ' ' * (indent * (depth_level + 1))
                print(key_spacing + Fore.YELLOW + str(key) + Fore.RESET + ': ', end='')
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
            print(prefix_spacing + Fore.GREEN + f'"{data}"')

        # Number
        elif isinstance(data, (int, float, complex)):
            print(prefix_spacing + Fore.BLUE + str(data))

        # Boolean
        elif isinstance(data, bool):
            print(prefix_spacing + Fore.LIGHTBLUE_EX + str(data))

        # None
        elif data is None:
            print(prefix_spacing + Fore.RED + 'None')

        # Other
        else:
            print(prefix_spacing + Fore.RESET + str(data))
        
        # Log to file
        if LogToFileLevel.PRETTY_PRINT in LogToFile._active_levels:
            formatted_data = ''
            try:
                formatted_data = json.dumps(data, indent=indent)
            except TypeError:
                formatted_data = str(data)
            LogToFile._log(formatted_data)
    
    @classmethod
    def table(cls, headers:list[str], rows:list[tuple], table_name:str=None) -> None:
        """
        **Format data into a table and print it.**

        *Parameters*:
        - `headers` (list[str]): The headers displayed in the table.
        - `rows` (list[tuple]): The rows displayed in the table.
        - `table_name` (str): The title name of the table.

        *Example*:
        ```python
        headers = ['Item', 'Stock', 'Price']
        rows = [('Cola', '25', '$2.99'), ('GPU', '3', '$995.00'), ('Feather', '2,500', '$0.29')]
        Log.table(headers, rows, table_name='Store Items')
        ```
        """
        column_lengths = { head: len(head) for head in headers }

        # Make sure row and header sizes match, and collect column sizes
        for row in rows:
            assert len(row) == len(headers), 'Header and row size is not matching!'

            for index, head in enumerate(headers):
                assert isinstance(row[index], str), 'An item in the row is not of type "str" !'
                length = len(row[index])
                if column_lengths[head] < length:
                    column_lengths[head] = length
        
        # Seperator function
        def seperator() -> None:
            seperators = ['-' * (column_lengths[head] + 6) for head in headers]
            _seperator = Fore.BLUE + 'X' + 'X'.join(seperators) + 'X'
            print(_seperator)
            if LogToFileLevel.TABLE in LogToFile._active_levels:
                LogToFile._log(escape_ansi(_seperator))

        # Print the title if passed
        if table_name:
            spacing = sum(column_lengths.values()) + len(headers) * 6 + (len(headers) + 11)
            title = Fore.BLUE + f'/  {Fore.YELLOW}{table_name}{Fore.BLUE}  \\'.center(spacing, '#')
            print(title)
            if LogToFileLevel.PRETTY_PRINT in LogToFile._active_levels:
                LogToFile._log(escape_ansi(title))

        seperator()

        # Print the headers
        formatted_headers = [Fore.YELLOW + head.center(column_lengths[head] + 6) for head in headers]
        finished_headers = Fore.BLUE + '|' + f'{Fore.BLUE}|'.join(formatted_headers) + Fore.BLUE + '|'
        print(finished_headers)
        if LogToFileLevel.PRETTY_PRINT in LogToFile._active_levels:
            LogToFile._log(escape_ansi(finished_headers))

        seperator()

        # Print the rows
        for index, row in enumerate(rows):
            # Space and print the rows
            spaced_row = [Fore.CYAN + item + ' '*(list(column_lengths.values())[index]-len(item)+5) for index, item in enumerate(row)]
            formatted_row = Fore.BLUE + '| ' + f'{Fore.BLUE}| '.join(spaced_row) + Fore.BLUE + '|'
            print(formatted_row)
            if LogToFileLevel.PRETTY_PRINT in LogToFile._active_levels:
                LogToFile._log(escape_ansi(formatted_row))
        
        seperator()