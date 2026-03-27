from typing import Union, Tuple, Optional, Callable, List, Dict, TYPE_CHECKING
import warnings
import copy

from .style import Style
from ..enums.color import Color

if TYPE_CHECKING:
    from ..context import Context


class Text:
    """
    Utility class to use minecraft text
    """

    text_bits: List["Text"]
    text: str
    color: Color
    styles: List[Style]
    hover_action: Optional[Tuple]
    click_action: Optional[Tuple]


    def __init__(
        self,
        text: Union[str, "Text"],
        color: Color = Color.White,
        *styles: Style
    ) -> None:
        """
        Creates a Json Text with the given text, color and styles supported by Minecraft
        """

        self.text_bits = []
        self.hover_action = None
        self.click_action = None
        
        if isinstance(text, Text):
            
            self.text = text.text
            self.color = text.color
            self.styles = text.styles
            self.hover_action = text.hover_action
            self.click_action = text.click_action
            self.text_bits = copy.deepcopy(text.text_bits)
        else:

            if not isinstance(text, str):
                text = str(text)
            
            if "'" in text or '"' in text:

                warnings.warn(f"Text `{text}` contains quotes! This migth cause issues and might not be displayed!")
                
                text = text.replace("'", "`")
                text = text.replace('"', "`")

            self.text = text
        
        self.color = color
        self.styles = list(styles)


    @property
    def plain_text(self) -> str:
        """
        Text plain text
        """

        t = self.text
        
        for item in self.text_bits:
            t += item.plain_text

        return t
    
    
    @staticmethod
    def _get_styles(d: Dict) -> List[Style]:

        styles = [Style.Obfuscated, Style.Bold, Style.Strikethrough, Style.Underlined, Style.Italic]
        text_styles = []

        for style in styles:
            if style.value in d.keys():
                text_styles.append(style)

        return text_styles

    
    @staticmethod
    def from_dict(d: Union[Dict, List]) -> "Text":
        
        if isinstance(d, List):
            
            t = [Text.from_dict(item) for item in d]

            main = t.pop(0)
            text = Text(main.text, main.color, *main.styles)
            text.text_bits.extend(t)

            return text

        color = Color.White

        if "color" in d.keys():
            color = d["color"]

        text = Text(d["text"], color, *Text._get_styles(d))

        if "hoverEvent" in d.keys():
            text.hover(d["hoverEvent"]["action"], d["hoverEvent"]["value"])
        if "clickEvent" in d.keys():
            text.click(d["clickEvent"]["action"], d["clickEvent"]["value"])

        return text


    def __len__(self) -> int:
        """
        The whole length of this text
        """

        l = len(self.text)

        for item in self.text_bits:
            l += len(item)

        return l
    

    def __deepcopy__(self, memo: Dict) -> "Text":

        cls = self.__class__
        result = cls.__new__(cls)
        
        memo[id(self)] = result

        result.text = self.text
        result.color = self.color
        result.styles = list(self.styles)
        
        result.text_bits = copy.deepcopy(self.text_bits, memo)
        
        result.hover_action = copy.deepcopy(self.hover_action)
        result.click_action = self.click_action

        return result


    def __add__(self, text: Union["Text", str]) -> "Text":
        
        inst = copy.deepcopy(self)

        if type(text) is Text:
            return inst(text)
        else:

            if len(inst.text_bits) > 0:
                
                tb = inst.text_bits[-1]

                if len(tb.styles) == 0 and tb.hover_action == () and tb.click_action == ():
                    tb.text += text # type: ignore
                    return inst
            
            elif len(inst.styles) == 0 and inst.hover_action == () and inst.hover_action == ():
                inst.text += text # type: ignore
                return inst
            
            color = inst.text_bits[-1].color if len(inst.text_bits) > 0 else inst.color
            return inst(Text(text, color))

    
    def __iadd__(self, other: Union["Text", str]) -> "Text":
        
        self = self.__add__(other)
        return self

    
    def __radd__(self, other: str) -> "Text":

        inst = copy.deepcopy(self)

        if len(inst.styles) == 0:
            inst.text = str(other) + inst.text
            return inst
        else:
            inst2 = copy.deepcopy(self)
            inst2.text_bits = []
            
            nt = Text(other, inst.color)
            nt.text_bits = [inst2, *inst.text_bits]
            
            return nt
        

    def __call__(self, text: "Text") -> "Text":
        """
        Appends the text
        """

        text_bits = text.text_bits
        t = copy.copy(text)
        t.text_bits = []
        
        self.text_bits.append(t)

        if len(text_bits) > 0:
            self.text_bits.extend(text_bits)
        
        return self


    def endl(self) -> "Text":
        """
        Appends a \\n at the end of this text
        """

        if len(self.text_bits) > 0:
            self.text_bits[-1].text += "\n"
        
        else:
            self.text += "\n"

        return self


    def format_hover_action(
        self,
        d: Dict,
        use_v1215_format: bool = False
    ) -> None:
        """
        Formats the hover action correctly, depending on the Minecraft version
        """

        if self.hover_action is None:
            return
        
        event_name = "hoverEvent"
        value_name = "value"

        if use_v1215_format:
            event_name = "hover_event"

            # I swear i have no idea what i've done here
            value_name = {
                "show_text": "value",
                "show_entity": "contents",
                "show_item": "contents"
            }[self.hover_action[0]]

        value = self.hover_action[1]
        
        if not isinstance(value, str):
            value = copy.deepcopy(value).to_json(use_v1215_format)
        
        d[event_name] = {
            "action": self.hover_action[0],
            value_name: value
        }


    def format_click_action(
        self,
        d: Dict,
        use_v1215_format: bool = False
    ) -> None:
        """
        Formats the click action correctly, depending on the Minecraft version
        """

        if self.click_action is None:
            return
        
        event_name = "clickEvent"
        value_name = "value"

        if use_v1215_format:
            event_name = "click_event"

            value_name = {
                "run_command": "command",
                "suggest_command": "command",
                "open_url": "url",
                "open_file": "path",
                "change_page": "page",
                "copy_to_clipboard": "value"
            }[self.click_action[0]]
        
        d[event_name] = {
            "action": self.click_action[0],
            value_name: self.click_action[1]
        }
    

    def to_json(
        self,
        use_v1215_format: bool = False,
        parent_styles: Optional[List[Style]] = None,
        original_color: Optional[Color] = None
    ) -> Union[Dict, List]:
        """
        Transforms this text (and all it's sub-components recursively) into a Dict or a List of Dict(s)
        """
        
        if parent_styles is None:
            parent_styles = []

        event_flag = False

        if (self.hover_action != () or self.click_action != ()) and len(self.text_bits) > 0:
            
            event_flag = True

            new_text = Text(self.text, self.color, *self.styles)
            new_text.hover_action = self.hover_action
            new_text.click_action = self.click_action

            self.text_bits.insert(0, new_text)
            self.text_bits.insert(0, Text(""))
        
        if len(self.text) > 0 and event_flag is False:

            d: Dict[str, Union[dict, str, bool]] = {"text": self.text}
            
            if original_color != None:

                if original_color != self.color:
                    d["color"] = self.color.value
            else:
                if self.color != Color.White: #TODO: Test this new bit
                    d["color"] = self.color.value
                
                original_color = self.color

            for style in set(self.styles): # Avoid duplicates
                d[style.value] = True
        
            for style in set(parent_styles): # Making sure that the precedent styles aren't applied here too
                if style not in self.styles:
                    d[style.value] = False

            self.format_hover_action(d, use_v1215_format)
            self.format_click_action(d, use_v1215_format)

        if len(self.text_bits) > 0:
            
            _list = []
            parent_styles = []
            styles_flag = False # Default styles needs to be set still

            if len(self.text) > 0 and event_flag is False:

                _list.append(d)
                parent_styles = self.styles
                styles_flag = True

            for item in self.text_bits:
                
                if len(item.text) > 0 or event_flag is True:

                    _list.append(
                        item.to_json( # type: ignore
                            use_v1215_format=use_v1215_format,
                            parent_styles=parent_styles,
                            original_color=original_color
                        )
                    )

                    if styles_flag is False:

                        parent_styles = item.styles
                        styles_flag = True
            
            return _list
        
        if not (len(self.text_bits) > 0 or len(self.text) > 0):
            return {"text": ""}

        return d
        

    def __str__(
        self,
        use_v1215_format: bool = False
    ) -> str:
        return str(copy.deepcopy(self).to_json(use_v1215_format)).replace("'", '"')

    
    def _split(self) -> list["Text"]:
        """
        Splits the list of texts into a list of texts that can be displayed in different lines,
        with multiple Rcon calls.
        """

        packets: List[Text] = []
        current_packet = Text("")

        parts_to_process = []

        if self.text:
            
            head = Text(self.text, self.color, *self.styles)
            head.hover_action = self.hover_action
            head.click_action = self.click_action
            parts_to_process.append(head)

        parts_to_process.extend(self.text_bits)

        for part in parts_to_process:
            
            if "\n" in part.text:
                
                sub_parts = part.text.split("\n")
                
                for i, sub_text in enumerate(sub_parts):

                    if sub_text:
                        
                        nt = Text(sub_text, part.color, *part.styles)
                        nt.hover_action = part.hover_action
                        nt.click_action = part.click_action
                        
                        if len((current_packet + nt).__str__(True)) > 1400:

                            packets.append(current_packet)
                            current_packet = nt
                        else:
                            current_packet += nt
                    
                    if i < len(sub_parts) - 1:
                        
                        if len(current_packet) > 0:
                            packets.append(current_packet)
                        
                        current_packet = Text("")
            else:
                
                if len((current_packet + part).__str__(True)) > 1400:

                    packets.append(current_packet)
                    current_packet = copy.deepcopy(part)

                else:
                    current_packet += part

        if len(current_packet) > 0:
            packets.append(current_packet)

        return packets

    
    def _set_same_color(self, color: Color) -> "Text":

        self.color = color

        for bit in self.text_bits:
            bit.color = color

        return self
        

    def black(self) -> "Text":
        """
        Colors all this text in black
        """

        return self._set_same_color(Color.Black)
    

    def dark_blue(self) -> "Text":
        """
        Colors all this text in dark_blue
        """
         
        return self._set_same_color(Color.DarkBlue)
    

    def dark_green(self) -> "Text":
        """
        Colors all this text in dark_green
        """
        
        return self._set_same_color(Color.DarkGreen)
    

    def dark_aqua(self) -> "Text":
        """
        Colors all this text in dark_aqua
        """
        
        return self._set_same_color(Color.DarkAqua)
    

    def dark_red(self) -> "Text":
        """
        Colors all this text in dark_red
        """
        
        return self._set_same_color(Color.DarkRed)
    

    def dark_purple(self) -> "Text":
        """
        Colors all this text in dark_purple
        """
        
        return self._set_same_color(Color.DarkPurple)
    

    def gold(self) -> "Text":
        """
        Colors all this text in gold
        """
        
        return self._set_same_color(Color.Gold)
    

    def gray(self) -> "Text":
        """
        Colors all this text in gray
        """
        
        return self._set_same_color(Color.Gray)
    

    def dark_gray(self) -> "Text":
        """
        Colors all this text in dark_gray
        """
        
        return self._set_same_color(Color.DarkGray)
    

    def blue(self) -> "Text":
        """
        Colors all this text in blue
        """
        
        return self._set_same_color(Color.Blue)
    

    def green(self) -> "Text":
        """
        Colors all this text in green
        """
        
        return self._set_same_color(Color.Green)
    

    def aqua(self) -> "Text":
        """
        Colors all this text in aqua
        """
        
        return self._set_same_color(Color.Aqua)
    

    def red(self) -> "Text":
        """
        Colors all this text in red
        """
        
        return self._set_same_color(Color.Red)
    

    def light_purple(self) -> "Text":
        """
        Colors all this text in ligth_purple
        """
        
        return self._set_same_color(Color.LightPurple)
    

    def yellow(self) -> "Text":
        """
        Colors all this text in yellow
        """
        
        return self._set_same_color(Color.Yellow)
    

    def white(self) -> "Text":
        """
        Colors all this text in white
        """
        
        return self._set_same_color(Color.White)


    def obfuscated(self) -> "Text":
        
        self.styles.append(Style.Obfuscated)
        return self
    

    def bold(self) -> "Text":
        
        self.styles.append(Style.Bold)
        return self
    

    def strikethrough(self) -> "Text":
        
        self.styles.append(Style.Strikethrough)
        return self
    

    def underlined(self) -> "Text":
        
        self.styles.append(Style.Underlined)
        return self
    

    def italic(self) -> "Text":
        
        self.styles.append(Style.Italic)
        return self

    
    def style(self, *styles: Style) -> "Text":

        self.styles.extend(list(styles))
        return self
    

    def gradient(
        self, 
        start_color: Color,
        end_color: Color
    ) -> "Text":
        """
        Colors the text with the gradient between the given colors
        """
        
        colors = [
            Color.Black, Color.Blue, Color.DarkGreen, Color.DarkAqua, Color.DarkRed, Color.DarkPurple,
            Color.Gold, Color.Gray, Color.DarkGray, Color.Blue, Color.Green, Color.Aqua, Color.Red,
            Color.LightPurple, Color.Yellow, Color.White
        ]

        steps = colors.index(end_color) - colors.index(start_color)

        steps = len(colors) + steps if steps <= 0 else steps

        for idx in range(steps):
            
            if len(self.text) >= idx*(steps + 1):
                s = self.text[idx*steps : idx*(steps + 1)]
            else:
                s = self.text[idx*steps : 0]
            
            self.text_bits.append(Text(s, colors[idx], *self.styles))

        self.text = ""

        return self

    
    def hover(
        self,
        show_text: Optional[Union[str, "Text"]] = None,
        show_entity: Optional[str] = None,
        show_item: Optional[str] = None
    ) -> "Text":
        """
        Sets the hover event.

        If you call this method without any keyword argument it will fallback with `show_text`.
        It's a nice shortcut sometimes, but not really a good practice
        """
        
        if show_text is not None:
            self.hover_action = "show_text", show_text

        elif show_entity is not None:
            self.hover_action = "show_entity", show_entity
            
        elif show_item is not None:
            self.hover_action = "show_item", show_item

        return self
    

    def click(
        self,
        suggest_command: Optional[str] = None,
        run_command: Optional[str] = None,
        run_function: Optional[Callable] = None,
        open_url: Optional[str] = None,
        copy_to_clipboard: Optional[str] = None,
        change_page: Optional[str] = None,
        open_file: Optional[str] = None
    ) -> "Text":
        """
        Sets the click event.

        Note: `run_function` is not officially implemented by Mojang, but handled by conduit itself
        """
        
        if suggest_command is not None:
            self.click_action = "suggest_command", suggest_command

        elif run_command is not None:
            self.click_action = "run_command", run_command

        elif run_function is not None:
            self.click_action = "run_function", run_function
            
        elif open_url is not None:
            self.click_action = "open_url", open_url

        elif copy_to_clipboard is not None:
            self.click_action = "copy_to_clipboard", copy_to_clipboard

        elif change_page is not None:
            self.click_action = "change_page", change_page

        elif open_file is not None:
            self.click_action = "open_file", open_file
            
        return self


def black(text: str) -> Text:
    
    return Text(text, Color.Black)


def dark_blue(text: str) -> Text:
    
    return Text(text, Color.DarkBlue)


def dark_green(text: str) -> Text:
    
    return Text(text, Color.DarkGreen)


def dark_aqua(text: str) -> Text:
    
    return Text(text, Color.DarkAqua)


def dark_red(text: str) -> Text:
    
    return Text(text, Color.DarkRed)


def dark_purple(text: str) -> Text:
    
    return Text(text, Color.DarkPurple)


def gold(text: str) -> Text:
    
    return Text(text, Color.Gold)


def gray(text: str) -> Text:
    
    return Text(text, Color.Gray)


def dark_gray(text: str) -> Text:
    
    return Text(text, Color.DarkGray)


def blue(text: str) -> Text:
    
    return Text(text, Color.Blue)


def green(text: str) -> Text:
    
    return Text(text, Color.Green)


def aqua(text: str) -> Text:
    
    return Text(text, Color.Aqua)


def red(text: str) -> Text:
    
    return Text(text, Color.Red)


def light_purple(text: str) -> Text:
    
    return Text(text, Color.LightPurple)


def yellow(text: str) -> Text:
    
    return Text(text, Color.Yellow)


def white(text: str) -> Text:
    
    return Text(text, Color.White)


def obfuscated(text: str) -> Text:
    
    return Text(text, Color.White, Style.Obfuscated)


def bold(text: str) -> Text:
    
    return Text(text, Color.White, Style.Bold)


def strikethrough(text: str) -> Text:
    
    return Text(text, Color.White, Style.Strikethrough)


def underlined(text: str) -> Text:
    
    return Text(text, Color.White, Style.Underlined)


def italic(text: str) -> Text:
    
    return Text(text, Color.White, Style.Italic)


def link(
    link: str,
    name_override: Optional[str] = None,
    hover: Union[str, Text] = "Click to open"
) -> Text:
    """
    Returns a `Text` instance with `name_override` (or just the link if its name_override its None) underlined 
    """

    if name_override is None:
        text = Text(link)
    else:
        text = Text(name_override)

    text.underlined()
    text.hover(show_text=hover)
    text.click(open_url=link)

    return text


def button(
    text: str,
    sound: Optional[str] = None,
    **hover_and_click_action: Union[str, Text, Callable],
) -> Text:
    """
    Creates a Text with the given text sorrounded by braces and underlined.

    You can also specify an hover and click action as you do in `Text.hover()` or `Text.click()`
    """

    btn = underlined(text=f"[{text}]")

    HOVER_ACTIONS = [
        "show_text",
        "show_item",
        "show_entity"
    ]

    CLICK_ACTIONS = [
        "suggest_command",
        "run_command",
        "run_function",
        "open_url",
        "copy_to_clipboard",
        "open_file"
    ]

    assert len(hover_and_click_action) <= 2

    def _get_action_name(action_names: List) -> Optional[str]:
            
        for item in hover_and_click_action:
            if item in action_names:
                return item

    hover = _get_action_name(HOVER_ACTIONS)

    if hover is not None:
        btn.hover(**{hover: hover_and_click_action[hover]}) # type: ignore
    
    click = _get_action_name(CLICK_ACTIONS)

    if click is not None:

        fn = hover_and_click_action[click]

        if sound is not None:

            def _fn(c: "Context"):

                c.server.execute(f"/execute at {c.player} run playsound {sound} ambient {c.player}")

                try:
                    fn(c)
                except Exception as e:
                    raise e
            
            btn.click(**{click: _fn}) # type: ignore

        else:
            btn.click(**{click: fn}) # type: ignore

    return btn


def suggester(
    *text: str,
    prefix: str,
    hover_fn: Optional[Callable[[str], Union[str, Text]]] = lambda x: f"Click to paste `{x}` in chat!"
) -> Text:
    """
    Suggests a list of words that you can click to paste in chat
    """

    st = Text(prefix)

    for i, txt in enumerate(text):
        
        t = " ".join(text[0:i+2])

        s = underlined(txt)

        if hover_fn is not None:
            s.hover(show_text=hover_fn(prefix+t))
        
        s.click(suggest_command=prefix+t)

        st += " "
        st += s

    return st


def quoted(text: Union[str, Text]) -> Union[str, Text]:
    """
    Wraps the given text with the valid quotation marks (`)
    """

    if isinstance(text, Text):
        return Text("`", text.color) + text + "`"
    
    return "`" + "`"