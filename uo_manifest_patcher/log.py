from enum import IntEnum, auto


class LogType(IntEnum):
    """Determines the severity or type of the log."""
    INFO = auto()
    DEBUG = auto()
    WARN = auto()
    ERROR = auto()


class Log:
    """Representation of a log used for printing information."""
    debug_mode: bool = False
    _last_len: int = 0

    @staticmethod
    def info(msg: str, end: str = '\n') -> None:
        """Creates a normal print log."""
        return Log.do(msg, end=end, logtype=LogType.INFO)

    @staticmethod
    def debug(msg: str, end: str = '\n') -> None:
        """Creates a debug log."""
        return Log.do(msg, end=end, logtype=LogType.DEBUG)

    @staticmethod
    def warn(msg: str, end: str = '\n') -> None:
        """Creates a warn log."""
        return Log.do(msg, end=end, logtype=LogType.WARN)

    @staticmethod
    def error(msg: str, end: str = '\n') -> None:
        """Creates an error log."""
        return Log.do(msg, end=end, logtype=LogType.ERROR)

    @staticmethod
    def do(msg: str, end: str = '\n',
           logtype: LogType = LogType.INFO) -> None:
        """Creates a log input, saving if it ends in a new line."""
        if logtype == LogType.INFO:
            Log._print(f"[{logtype.name.lower()}] {msg}", end=end)
        if logtype == LogType.DEBUG:
            Log._debug(f"[{logtype.name.lower()}] {msg}", end=end)
        if logtype == LogType.WARN:
            Log._warn(f"[{logtype.name.lower()}] {msg}", end=end)
        if logtype == LogType.ERROR:
            Log._error(f"[{logtype.name.lower()}] {msg}", end=end)

        # Ignore in-line messages.
        if end != '\n':
            return

    @staticmethod
    def clear() -> None:
        """Clears the current line, this is used on updating text."""
        print(' ' * Log._last_len, end='\r')

    @staticmethod
    def _print(text: str, end: str = '\n') -> None:
        """Prints text to console. By default, it creates a new line.
        Passing '\r' makes it return the cursor to the beginning of the line.
        """
        diff: int = Log._last_len - len(text)
        extra = ''
        if diff > 0:
            extra = ' ' * diff
        print(f"{text}{extra}", end=end)
        Log._last_len = len(text)

    @staticmethod
    def _debug(text: str, end: str = '\n') -> None:
        """Only prints the text passed if debug mode is currently set."""
        if not Log.debug_mode:
            return
        Log._print(text, end=end)

    @staticmethod
    def _warn(text: str, end: str = '\n') -> None:
        """Prints text in the event of an error."""
        Log._print(text, end=end)

    @staticmethod
    def _error(text: str, end: str = '\n') -> None:
        """Prints text in the event of an error."""
        Log._print(text, end=end)
