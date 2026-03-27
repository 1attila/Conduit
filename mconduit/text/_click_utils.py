import sys


class same_function():
    """
    Context manager that binds the click methods with the same function and scoreboard.

    This means that the function id will increase by 1 every new click event bounds that function, to be able to determine exactly what part of the text is calling that event
    """


    def __enter__(self) -> None:

        self._text = sys.modules["text"]
        setattr(self._text, "__enable_same_function", True)


    def __exit__(self, exc_type, exc_value, traceback) -> None:
        
        setattr(self._text, "__enable_same_function", False)