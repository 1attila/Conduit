from ..text import Text


class Score:
    """
    This probably won't be used, it's just the real representation of what's inside the 
    List[Score].

    Its data will be merged inside scoreboard
    """


    def __init__(
        self,
        score: int,
        name: str,
        objective: str,
        locked: bool,
        display: Text,
        format: str
    ) -> None:
        ...
