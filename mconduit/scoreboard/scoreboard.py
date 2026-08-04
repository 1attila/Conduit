from typing import Optional, Tuple, Dict, TYPE_CHECKING
from abc import ABC
import copy

from mconduit.text.text import Text
from mconduit._types.player import Player

if TYPE_CHECKING:
    from mconduit.server_api import ServerAPI


class DisplayFormat(ABC):
    """
    Abstract class that represents a scoreboard number format

    It could be:

    - Blank

    - Fixed

    - Styled
    """


class Blank(DisplayFormat):
    """
    Doesnt display any value
    """


class Fixed(DisplayFormat):
    """
    Displays a fixed Text
    """


    value: Text


    def __init__(
        self,
        value: Text
    ) -> None:
        
        self.value = value


class Styled(DisplayFormat):
    """
    Displayed the value with the given styles
    """


    style: Text


    def __init__(
        self,
        style: Text
    ) -> None:
        
        self.style = style


class Scoreboard:
    """
    Represents a Minecraft scoreboard
    """


    _objective: str
    _display: Optional[Text]
    _format: Optional[DisplayFormat]
    _scores: Dict[str, Tuple[int, bool]]
    _server: "ServerAPI"


    def __init__(
        self,
        objective: str,
        display: Optional[Text],
        format: Optional[DisplayFormat],
        scores: Dict[str, Tuple[int, bool]],
        *,
        server: "ServerAPI"
    ) -> None:
        
        self._objective = objective
        self._display = display
        self._format = format
        self._scores = scores

        self._server = server


    @property
    def objective(self) -> str:
        """
        Objective criteria name
        """

        return self._objective
    

    @property
    def display(self) -> Optional[Text]:
        """
        Text used to display this scoreboard
        """

        return copy.copy(self._display)


    @property
    def format(self) -> Optional[DisplayFormat]:
        """
        Score display format
        """

        return self._format


    @property
    def scores(self) -> Dict[str, Tuple[int, bool]]:
        """
        Maps player-name to its score and locked value
        """

        return dict(self._scores)


    def __getitem__(
        self,
        key: Player | str
    ) -> int:
        
        if isinstance(key, Player):
            key = key.name

        return self._scores[key][0]
    

    def get(
        self,
        key: Player | str,
        default: Optional[int] = None
    ) -> Optional[int]:
        
        try:    
            return self[key]
        
        except KeyError:
            return default


    def is_locked_for(self, key: Player | str) -> bool:

        if isinstance(key, Player):
            key = key.name

        return self._scores.get(key, (0, False))[1]


    def create(self) -> None:
        raise NotImplementedError

    
    def delete(self) -> None:
        raise NotImplementedError