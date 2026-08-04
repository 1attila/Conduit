# type: ignore

from typing import Dict, List, Tuple, Optional, TYPE_CHECKING
from functools import lru_cache
import copy
import enum

from mconduit.text.text import Text

if TYPE_CHECKING:
    from mconduit._types.message import Message


MINECRAFT_FONT_WIDTHS = {
    " ":63, "A":84, "B":84, "C":84, "D":84, "E":84, "F":84,
    "G":84, "H":84, "I":56, "J":84, "K":84, "L":84, "M":84,
    "N":84, "O":84, "P":84, "Q":84, "R":84, "S":84, "T":84,
    "U":84, "V":84, "W":84, "X":84, "Y":84, "Z":84,
    "a":84, "b":84, "c":84, "d":84, "e":84, "f":70, "g":84,
    "h":84, "i":21, "j":84, "k": 72, "l":21, "m":84, "n":84,
    "o":84, "p":84, "q":84, "r":84, "s":84, "t":63, "u":84,
    "v":84, "w":84, "x":84, "y":84, "z":84,
    "0":84, "1":84, "2":84, "3":84, "4":84, "5":84,
    "6":84, "7":84, "8":84, "9":84,

    ".":28, ",":28, ":":28, ";":28, "!":28, "?":84, "'":28,
    '"':56, "/":84, "\\":24, "|":28, "-":84, "_":84, "+":84,
    "=":84, "*": 63, "&":84, "%":84, "#":84, "@":98, "^":84,
    "~": 98, "`":14, "(":56, ")":56, "[":56, "]":56, "{":56,
    "}":56, "<": 72, ">": 72, "\u2003": 70
}

class _Approx(enum.Enum):
    less =  enum.auto()
    more =  enum.auto()
    unset = enum.auto()


class DisplayMode(enum.Enum):
    """
    Table display mode
    
    Horizontal
    ```
    | key | item |
    | a   | 1    |
    | b   | 2    |
    ```

    Vertical
    ```
    | key  | a | b |
    | item | 1 | 2 |
    ```

    Map
    ```
    |   | 1 | 2 |
    | a | X | O |
    | b | O | X |
    ```
    """

    Horizontal = enum.auto()
    Vertical =   enum.auto()
    Map =        enum.auto()


class Alignment(enum.Enum):
    """
    Controls the text position inside it's box:

    Center:
    ```
    | key | item |
    | a   | 1    |
    | b   | 2    |
    ```
    
    Left:
    ```
    |key |item |
    |a   |1    |
    |b   |2    |
    ```

    Rigth
    ```
    | key| item|
    | a  | 1   |
    | b  | 2   |
    ```
    """

    Center = enum.auto()
    Left =   enum.auto()
    Right =  enum.auto()


class Table:

    """
    Represent a Text table that can be sent in chat
    """
    

    title: "Message"
    _rows: Optional[int]
    _columns: Optional[int]
    mode: DisplayMode
    __container: List["Message"]


    def __init__(self,
                 title: "Message"="",
                 rows: Optional[int]=None,
                 columns: Optional[int]=None,
                 mode: DisplayMode=DisplayMode.Horizontal
                 ) -> "Table":
        """
        Creates a Table with the given parameters
        """

        if mode == DisplayMode.Horizontal:
            assert columns is not None

        elif mode == DisplayMode.Vertical:
            assert rows is not None

        else: # DisplayMode.Map
            assert rows is not None and columns is not None

        self.title = title
        self._rows = rows
        self._columns = columns
        self.mode = mode
        self.__container = []


    @property
    def data(self) -> List["Message"]:
        """
        Table datas
        """

        return self.__container


    @data.setter
    def data(self, values: List) -> None:
        """
        Table data setter.

        You should use this only with DisplayMode.Map
        """

        self.__container = values


    @property
    def columns(self) -> int:
        """
        Table columns
        """

        if self.mode == DisplayMode.Vertical:
            self._columns = len(self.__container) // self._rows

        return self._columns


    @property
    def rows(self) -> int:
        """
        Table rows
        """

        if self.mode != DisplayMode.Vertical:
            self._rows = len(self.__container) // self._columns

        return self._rows


    @staticmethod
    def from_dict(d: Dict, keys_name: str="", item_name: str="", mode: DisplayMode=DisplayMode.Horizontal) -> "Table":
        """
        Creates a Table from the given 
        """
        
        d = {"a": 1, "b": 2}

        """
        HORIZONAL
        | keys  | item |
        | a     | 1    |
        | b     | 2    |
        """

        """
        VERTICAL
        | keys | a | b |
        | item | 1 | 2 |
        """
        
        ...


    @staticmethod
    def as_map_from(value: Dict, title: "Message", up_left_box: "Message"="") -> "Table":
        """
        Creates a Map Table

        The dict must have 2 entries, like this one:
        ```
        {
            "A": { "1": "X", "2": "O", "3": "X" },
            "B": { "1": "O", "2": "X", "3": "O" },
            "C": { "1": "X", "2": "O", "3": "X" },
        }
        ```
        To generate a map like this:
        ```
        |   | 1 | 2 | 3 |
        | A | X | O | X |
        | B | O | X | O |
        | C | X | O | X |
        ```
        The second entries must have the same keys name
        """
        ...


    def insert(self, *values) -> "Table":
        """
        Insert a row or column, depending on the mode
        """
        
        if self.mode == DisplayMode.Horizontal:
            assert len(values) == self._columns

        elif self.mode == DisplayMode.Vertical:
            assert len(values) == self._rows
        else:
            raise RuntimeError("You cant insert items in Table with DisplayMode.Map")
        
        if self.mode == DisplayMode.Vertical:
            
            self._columns = len(self.__container) // self._rows

            for i, item in enumerate(values):
                self.__container.insert(self._columns + i * (self._columns + 1), item)

        else:
            self.__container.extend(values)

        return self

    
    def _len(self, text: str) -> int:

        return sum([MINECRAFT_FONT_WIDTHS.get(item, 84) for item in text])


    def _visible_width(self, cell: "Message") -> int:
        print("vw", cell)
        if isinstance(cell, str):
            return self._len(cell)
        print(cell.text_bits)
        return self._len(cell.plain_text)


    def _repeat_char(self, c: str, target_width: int) -> str:
    
        result = ""

        while self._len(result) < target_width:
            result += c

        return result

    
    def _repeat_space(self, target_width: int) -> str:
        """
        Returns a string with the space with the most near width
        """

        a, b, _app = self._approx_as_sum(target_width)

        return "\u2003" * a + " " * b

        
    @lru_cache()
    def _approx_as_sum(self, target_width: int, approx: _Approx=_Approx.more) -> Tuple[int, int, _Approx]:
        """
        Finds the best approximation of target_width as a sum of 70s and 63s

        `target_width ≈ a*70 + b*63`
        """

        differences = []
        coefficient_pairs = []
        max_a = target_width // 70 + 1
        max_b = target_width // 63 + 1

        for a in range(max_a + 1):
            for b in range(max_b + 1):

                approx_value = a * 70 + b * 63

                diff = abs(target_width - approx_value)

                if diff == 0:
                    return a, b, _Approx.unset

                differences.append(diff)
                coefficient_pairs.append((a, b))

        if approx == _Approx.unset:

            best_diff = float("inf")

            for diff in differences:
                best_diff = min(best_diff, abs(diff))

            approx = _Approx.more if best_diff > 0 else _Approx.less

            return *coefficient_pairs[differences.index(best_diff)], approx

        if approx == _Approx.more:
            
            best_diff = float("inf")

            for diff in differences:
                if diff < 0:
                    continue
                
                if diff < best_diff:
                    best_diff = diff 
            
            return *coefficient_pairs[differences.index(best_diff)], _Approx.more
        
        best_diff = float("-inf")

        for diff in differences:

            if diff > 0:
                continue

            if diff > best_diff:
                best_diff = diff

        return coefficient_pairs[differences.index(best_diff)], best_diff, _Approx.less
    

    def _front_text(self, text: "Message", item: str) -> "Message":
        """
        Appends something to the front of the text        
        """

        if type(text) is str:
            return item + text
        
        t = copy.deepcopy(text)
        tex = text.text

        t.text = ""

        return Text(item) + t + tex
    

    def _align(self, cell: "Message", size: int, alignment: Alignment) -> Tuple["Message", int]:
        """
        Aligns the text in the message based on the cell size
        """

        remaining_space = size - self._visible_width(cell)
        
        if remaining_space == 0:
            return cell, 0
        
        elif remaining_space > 0:
            
            def center_align() -> Tuple[str, str]:

                if remaining_space % 2 == 0:
                    side = self._repeat_space(remaining_space // 2)
                    
                    return side, side
                
                n = remaining_space // 2
                
                return self._repeat_space(n + 1), self._repeat_space(n)

            left, rigth = {
                Alignment.Center: center_align(),
                Alignment.Right: ("", self._repeat_space(remaining_space)),
                Alignment.Left: (self._repeat_space(remaining_space), "")
            }[alignment]

            diff = remaining_space - self._len(left + rigth)
            
            if type(cell) is str:
                print("OK")
                return left + cell + rigth, diff
            else:
                t = Text(left) + cell + rigth
                print(t)
                return Text(left) + cell + rigth, diff
        
        text = cell if type(cell) is str else cell.text

        text = text[0:size-3] + "..."
        
        if type(cell) is str:
            return text
        
        else:
            t = cell.text = ""
            return t + text

        
    def _draw_column(self, messages: List["Message"], cells: List["Message"], size: int, regions_width: List[int], draw_columns: bool, alignment: Alignment) -> Tuple[List["Message"], List[int]]:
        
        new_offsets = [0] * self.rows

        for i, cell in enumerate(cells):
            
            cells[i], new_offsets[i] = self._align(cell, size + regions_width[i], alignment)
            
        max_diff = max(new_offsets) - min(new_offsets)
        max_len = max(self._visible_width(item) for item in cells)

        if abs(max_diff) > 7: # 7 is the min fix possible

            for i, cell in enumerate(cells): # Rounding everything for eccess
                cells[i], new_offsets[i] = self._align(cells[i], max_len, alignment)

        for i, message in enumerate(messages):
            messages[i] = message + cells[i]

        if draw_columns is True:

            for i, _m in enumerate(messages):
                messages[i] = messages[i] + "|"

        return messages, new_offsets

    
    def _draw_horizontal(self, char_space, alignment, max_row_length, draw_columns, draw_rows) -> List["Message"]:
        
        columns_width = []

        for column in range(self.columns):
            
            c = self.__container[column :: self.columns]

            max_item_len = max(self._visible_width(item) for item in c)
            max_item_len += 2 * self._len(char_space)

            columns_width.append(max_item_len)

        max_row_len = sum(columns_width)

        if draw_columns is True:
            max_row_len += self.columns + 1
        
        if max_row_len > max_row_length: # Strip something
            ...

        out_messages = []
        
        """ if len(self.title) > 0:
            out_messages.append(self._align(self.title, max_row_len, alignment)[0]) """
        
        for row in range(self.rows):
            out_messages.append(Text("|" if draw_columns is True else ""))

        """ if draw_rows is True:

            row_line = Text(self._repeat_char("-", max_row_len))

            for i in range(start=1, stop=len(self.rows), step=2):
                out_messages[i] = row_line """

        offsets = [0] * self.rows

        for c in range(self.columns):

            out_messages, offsets = self._draw_column(
                out_messages,
                self.__container[c::self.columns],
                columns_width[c],
                offsets,
                draw_columns,
                alignment
            )

        return out_messages


    def _draw_horizontal2(self, char_space, alignment, max_row_length, draw_columns, draw_rows) -> List["Message"]:
        
        columns_width = []

        for column in range(self.columns):
            
            c = self.__container[column :: self.columns]

            max_item_len = max(self._visible_width(item) for item in c)
            max_item_len += 2 * self._len(char_space)

            columns_width.append(max_item_len)

        max_row_len = sum(columns_width)

        if draw_columns is True:
            max_row_len += self.columns + 1
        
        if max_row_len > max_row_length: # Strip something
            ...

        out_messages = []
        
        if len(self.title) > 0:
            out_messages.append(self._align(self.title, max_row_len, alignment)[0])
        
        if draw_rows is True:

            row_line = Text(self._repeat_char("-", max_row_len))

            out_messages.append(row_line)

        for row in range(self.rows):
            
            r = "|" if draw_columns else ""
            r = Text(r)
            offset = 0

            for item in range(self.columns):

                t, offset = self._align(
                    self.__container[row * self.columns + item],
                    columns_width[item] + offset,
                    alignment
                )

                r = r + t
            
                if draw_columns:
                    r = r + "|"

            out_messages.append(r)

            if draw_rows is True:
                out_messages.append(row_line)

        return out_messages
        

    def _draw_vertical(self, char_space, alignment, max_row_length) -> List["Message"]:
        
        columns_width = []

    def _draw_map(self, char_space, alignment, max_row_length) -> List["Message"]:
        ...


    def draw(
            self,
            char_space=" ",
            draw_rows: bool=True,
            draw_columns: bool=True,
            alignment: Alignment=Alignment.Center,
            max_row_lenght: int=64
            ) -> List["Message"]:
        """
        Transforms everythin in a list of Messages ready to be printed

        Note:
        Since the chat has a max row length of 64, if this is limit is exceeded, the table will be cut in this way:
        
        - If theres
        """
        
        
        return {
            DisplayMode.Horizontal: self._draw_horizontal,
            DisplayMode.Vertical: self._draw_horizontal,
            DisplayMode.Map: self._draw_map
        }[self.mode](char_space, alignment, max_row_lenght, draw_columns, draw_rows)