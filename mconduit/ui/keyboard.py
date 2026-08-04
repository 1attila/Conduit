from typing import Union, Callable, List, Any

from mconduit.text import Text
from mconduit.context import Context
from mconduit._types import Player
from mconduit import sound


class _Key:
    """
    Stores key data
    """

    def __init__(
        self,
        display: str,
        *,
        other_keys: Union[List[str], str, None] = None,
        suggesters: Union[List[str], str, None] = None
    ) -> None:
        """
        Parameters:

        - display: main key that will be displayed between brackets e.g. "2" -> "[2]".

        - other_keys: suggests those keys when you hover this key.

        - suggesters: overwrites the default suggester which is [display] + other_keys
        """
        
        self.display = display

        if type(other_keys) is not list:
            other_keys = [other_keys]

        self.other_keys = other_keys

        if suggesters is None:
            self.suggesters = [display]
            
            if other_keys is not None:
                self.suggesters += other_keys
        else:
            
            if type(suggesters) is not list:
                self.suggester = [suggesters]


def _is_special_char(character: str) -> bool:

    if character.lower() == character.upper():
        return True

    return False


ROW_0 = [
    _Key("|"),
    _Key("1", other_keys="!"),
    _Key("2"),
    _Key("3", other_keys="£"),
    _Key("4", other_keys="$"),
    _Key("5", other_keys="%"),
    _Key("6", other_keys="&"),
    _Key("7", other_keys="/"),
    _Key("8", other_keys="("),
    _Key("9", other_keys=")"),
    _Key("0", other_keys="="),
    _Key("'", other_keys="?"),
    _Key("ì", other_keys="^"),
    _Key("<--", suggesters="Cancel")
]

ROW_1 = [
    _Key("TAB", suggesters="Tab"),
    _Key("Q"),
    _Key("W"),
    _Key("E", other_keys="€"),
    _Key("R"),
    _Key("T"),
    _Key("Y"),
    _Key("U"),
    _Key("I"),
    _Key("O"),
    _Key("P"),
    _Key("è", other_keys=["é", "[", "{"]),
    _Key("+", other_keys=["*", "]", "}"]),
    _Key("ù", other_keys="§")
]

ROW_2 = [
    _Key("LOCK", suggesters="Cap lock"),
    _Key("A"),
    _Key("S"),
    _Key("D"),
    _Key("F"),
    _Key("G"),
    _Key("H"),
    _Key("J"),
    _Key("K"),
    _Key("L"),
    _Key("ò", other_keys=["ç", "@"]),
    _Key("à", other_keys=["°", "#"]),
    _Key("", suggesters="New line")
]

ROW_3 = [
    _Key("", suggesters="Shift"),
    _Key("Z"),
    _Key("X"),
    _Key("C"),
    _Key("V"),
    _Key("B"),
    _Key("N"),
    _Key("M"),
    _Key(",", other_keys=";"),
    _Key(".", other_keys=":"),
    _Key("-", other_keys=["_"]),
    _Key("PAUSE", suggesters="Pause & shift")
]

ROW_4 = [
    _Key("CTRL"),
    _Key("ALT"),
    _Key("     SPACE     ", suggesters="Space"),
    _Key("<", other_keys=">"),
    _Key("<<", suggesters="Cursor Left"),
    _Key(">>", suggesters="Cursor Right")
]

ALL_KEYS = ROW_0 + ROW_1 + ROW_2 + ROW_3 + ROW_4
CANCEL_ID = 13
TAB_ID = 14
NEW_LINE_ID = 40
SHIFT_ID = 41
SHIFT_PAUSE_ID = 52
CTRL_ID = 53
ALT_ID = 54
SPACE_ID = 55


class Keyboard:
    """
    Chat Keyboard.

    Useful for getting secret inputs
    """


    _input: str
    _shift_enabled: bool
    _ctrl_enabled: bool
    _alt_enabled: bool
    _cap_enabled: bool
    _cursor_pos: int
    callback: Callable[[str], Any]


    def __init__(self) -> None:
        
        self._input = ""
        self._shift_enabled = False
        self._ctrl_enabled = False
        self._alt_enabled = False
        self._cap_enabled = False
        self._cursor_pos = 0


    def _caps_enabled(self) -> bool:
        
        return self._shift_enabled != self._cap_enabled

    
    def _insert_text(self, text: str) -> None:

        assert len(text) == 1

        characters = list(self._input)
        characters.insert(self._cursor_pos, text)

        self._input = "".join(characters)
        self._cursor_pos += 1


    def _on_click(self, ctx: Context):
        
        ctx.server.execute(f"execute at {ctx.player.name} run playsound {sound.entity.arrow.hit_player}")
        
        match ctx.id:

            case 13: # CANCEL_ID
                
                if len(self._input) > 0:
                    self._input = self._input[:-2]
                return
            
            case 14: # TAB_ID
                self._input += " " * 4
                return

            case 40: # NEW_LINE_ID
                self._input += "\n"
                return

            case 41: # SHIFT_ID
                self._shift_enabled = not self._shift_enabled
                return

            case 52: # SHIFT_PAUSE_ID
                self._shift_enabled = not self._shift_enabled
                return

            case 53: # CTRL_ID
                self._ctrl_enabled = not self._ctrl_enabled
                return

            case 54: # ALT_ID
                self._alt_enabled = not self._alt_enabled
                return

            case 55: # SPACE_ID
                self._input += " "
                return

        character: _Key = (ROW_0 + ROW_1 + ROW_2 + ROW_3 + ROW_4)[ctx.id]
        char = character.display

        if (
            self._shift_enabled is True and
            self._ctrl_enabled is True and
            self._alt_enabled is True
        ):

            if len(character.other_keys) > 2:

                self._input += character.other_keys[2]
                return

        if (
            self._ctrl_enabled is True and
            self._alt_enabled is True
        ):

            if len(character.other_keys) > 1:

                self._input += character.other_keys[1]
                return

        if self._cap_enabled():
            
            if _is_special_char(char):
                char = character.other_keys[0]
            else:
                char = char.upper()

            self._input += char
            return

        self._input += char.lower()

    
    def draw(
        self,
        player: Union[str, Player],
        colour
    ) -> List[Text]:

        lines = []
        rows = [ROW_0, ROW_1, ROW_2, ROW_3]

        for row in rows:

            line = Text(colour=colour)

            for key in row:
                
                btn = Text(f"[{key.display}]", colour=colour)

                hover_text = ""

                for i, suggestion in enumerate(key.suggesters):

                    if 1 < i < len(hover_text) + 1:
                        hover_text += "\n"

                    hover_text += "\u2001" * i + suggestion

                btn.hover(show_text=hover_text)
                btn.click(run_function=self._on_click)

                line += btn

            lines.append(line)

        return lines


    def display(
        self,
        player: Player,
        callback: Callable[[str], Any]
    ) -> None:
        """
        Enables player typing
        """

        self.draw(player, colour="gray")
        self.callback = callback