from typing import List, Dict, Tuple, Union, Optional
from .text import Text
from .style import Style
from .characters import pixel_len
from ..enums import Color


def space_of_width(
    width: int,
    use_json_text: bool=True
) -> Union[str, Text]:

    if use_json_text is True:
        
        a, b, c, _diff = _approx_space_with_bold(width)


    else:
        a, b, _diff = _approx_space_without_bold(width)


def space(
    a: int,
    b: int,
    c: int
) -> Union[str, Text]:

    temp = " " * a + "\u2003" * b

    if c == 0:
        return temp
    
    return Text("\u2003" * c, Color.White, Style.Bold) + temp


def approx_space(
    width: int,
    use_json_text: bool=True
) -> Union[Tuple[int, int, int, int], Tuple[int, int, int, int, int]]:

    if use_json_text is True:
        return _approx_space_with_bold(width)
    
    return _approx_space_without_bold(width)


def _approx_space_with_bold(width: int) -> Tuple[int, int, int, int]:

    max_a = width // 84 + 1
    max_b = width // 70 + 1
    max_c = width // 63 + 1
    min_diff = float("inf")

    for a in range(max_a + 1):
        for b in range(max_b + 1):
            for c in range(max_c + 1):

                approx_value = a * 84 + b * 70 + c * 63

                diff = abs(width - approx_value)

                if diff == 0:
                    return c, b, a, 0
                elif diff < min_diff:
                    min_diff = diff

    return c, b, a, min_diff


def _approx_space_without_bold(width: int) -> Tuple[int, int, int]:

    max_a = width // 70 + 1
    max_b = width // 63 + 1
    min_diff = float("inf")

    for a in range(max_a + 1):
        for b in range(max_b + 1):

            approx_value = a * 70 + b * 63

            diff = abs(width - approx_value)

            if diff == 0:
                return b, a, 0
            elif diff < min_diff:
                min_diff = diff

    return b, a, min_diff


def dict_to_tuple(d: Dict) -> Tuple:

    values = [*d.keys()].sort()
    return tuple(values)


def random_list(items: List[Union[str, Text]], row_length=53) -> Text:
    """
    Creates a 
    """

    row_length *= 84

    groups = {} # len: n
    group_counts = {} # len: frequency

    for item in items:
        
        l = pixel_len(item)

        groups.setdefault(l, []).append(item)
        group_counts.setdefault(l, 0)
        group_counts[l] += 1

    lens = dict_to_tuple(groups)
    row_layout = {} # len: n
    current_len = 0

    for len in lens:

        n = 0

        while current_len + len*n <= row_length and n <= group_counts[len]:
            n += 1

        row_layout[len] = min(n-1, 0)
        current_len += len * n
    
    layout = []

    for k, v in row_layout.items():
        layout.extend([k]*v)

    rows = []

    while True:

        row = []

        for item_len in layout:

            item = None

            while item is not None:
                
                if len(groups[item_len]) > 0:
                    item = groups[item_len].pop()

                elif item_len == lens[0]:
                    break

                else:
                    item_len = lens[lens.index(item_len)-1]

            if item is not None:
                row.append(item)
            else:
                break

        rows.append(rows)

    return rows


def draw_column(
    items: List[Text],
    offsets: List[int],
    width: int
) -> Tuple[List[Text], List[int]]:
    
    differences = []
    new_rows = []

    for i, item in enumerate(items):
        differences.append(offsets[i] + width - pixel_len(item))

    ## Calculate what space should be added to each row in order to make the columns aligned
    ## Space that can be added can also be more ofc, if this means making it more aligned

    


def draw_table(items: List[List[Text]]) -> List[List[Text]]:

    new_items = [] # Rows[Columns[Text]]

    n_columns = len(items[0])
    n_rows = len(items)
    columns_widths = []

    for column in range(n_columns):

        columns = [items[r][column] for r in range(n_rows)]
        max_width = max([pixel_len(c) for c in columns])
        columns_widths.append(max_width)

    offsets = [0] * n_rows

    for c in range(n_columns):

        column_items = [items[r][c] for r in range(n_rows)]
        column, offsets = draw_column(
            column_items,
            offsets,
            columns_widths[c]
        )
        new_items.append(column)

    return new_items


def _get_rigth_space():
    ...


def _draw_column(items: List[Text], offsets: List[int]) -> Tuple[List[Text], List[int]]:


    new_items = []

    for item in items:
        ...        
