from typing import Union, Tuple, Optional, NoReturn, List, Dict
import copy

from .Action import HoverAction, ClickAction
from .Style import Style
from ..Enums.Color import Color


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


    def __init__(self, text: Union[str, "Text"], color: Color=Color.White, *styles: Style) -> NoReturn:

        self.text_bits = []
        self.hover_action = None
        self.click_action = None
        
        if isinstance(text, str):
            self.text = text
        else:
            self.text = text.text
            self.color = text.color
            self.styles = text.styles
            self.hover_action = text.hover_action
            self.click_action = text.click_action
            self.text_bits = copy.deepcopy(text.text_bits)
        
        self.color = color
        self.styles = list(styles)

    
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
            text = Text(main.text, main.color, main.styles)
            text.text_bits.insert(t)

            return text

        color = Color.White

        if "color" in d.keys():
            color = d["color"]

        text = Text(d["text"], color, Text._get_styles(d))

        if "hoverEvent" in d.keys():
            text.hover(d["hoverEvent"]["action"], d["hoverEvent"]["value"])
        if "clickEvent" in d.keys():
            text.click(d["clickEvent"]["action"], d["clickEvent"]["value"])

        return text


    def __add__(self, text: "Text") -> "Text":
        return self(text)
    

    def __call__(self, text: "Text") -> "Text":
        """
        Appends the text
        """
        
        text_bits = text.text_bits
        t = copy.deepcopy(text)
        t.text_bits = []

        self.text_bits.append(t)

        if len(text_bits) > 0:
            self.text_bits.extend(text_bits)
        
        return self


    def to_json(self) -> Union[Dict, List]:
        
        d = {"text": self.text}

        if self.color != Color.White:
            d["color"] = self.color.value

        for style in set(self.styles): # Avoid duplicates
            d[style.value] = True

        if self.hover_action:
            d["hoverEvent"] = {
                "action": self.hover_action[0].value,
                "value": self.hover_action[1]
            }

        if self.click_action:
            d["clickEvent"] = {
                "action": self.click_action[0].value,
                "value": self.click_action[1]
            }

        if len(self.text_bits) > 0:
            list = [item.to_json() for item in self.text_bits]
            list.insert(0, d)

            return list
        
        return d
        

    def __str__(self) -> str:
        return str(self.to_json()).replace("'", '"')
        

    def black(self) -> "Text":

        self.color = Color.Black
        return self
    

    def dark_blue(self) -> "Text":

        self.color = Color.DarkBlue
        return self
    

    def dark_green(self) -> "Text":
        
        self.color = Color.DarkGreen
        return self
    

    def dark_aqua(self) -> "Text":
        
        self.color = Color.DarkAqua
        return self
    

    def dark_red(self) -> "Text":
        
        self.color = Color.DarkRed
        return self
    

    def dark_purple(self) -> "Text":
        
        self.color = Color.DarkPurple
        return self
    

    def gold(self) -> "Text":
        
        self.color = Color.Gold
        return self
    

    def gray(self) -> "Text":
        
        self.color = Color.Gray
        return self
    

    def dark_gray(self) -> "Text":
        
        self.color = Color.DarkGray
        return self
    

    def blue(self) -> "Text":
        
        self.color = Color.Blue
        return self
    

    def green(self) -> "Text":
        
        self.color = Color.Green
        return self
    

    def aqua(self) -> "Text":
        
        self.color = Color.Aqua
        return self
    

    def red(self) -> "Text":
        
        self.color = Color.Red
        return self
    

    def ligth_purple(self) -> "Text":
        
        self.color = Color.LigthPurple
        return self
    

    def yellow(self) -> "Text":
        
        self.color = Color.Yellow
        return self
    

    def white(self) -> "Text":
        
        self.color = Color.White
        return self


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

        self.styles.extend(styles)
        return self
    

    def gradient(self, start_color: Color, end_color: Color) -> "Text":
        
        colors = [
            Color.Black, Color.Blue, Color.DarkGreen, Color.DarkAqua, Color.DarkRed, Color.DarkPurple,
            Color.Gold, Color.Gray, Color.DarkGray, Color.Blue, Color.Green, Color.Aqua, Color.Red,
            Color.LigthPurple, Color.Yellow, Color.White
        ]

        steps = colors.index(end_color) - colors.index(start_color)

        steps = len(colors) + steps if steps <= 0 else steps

        for idx in range(steps):
            
            if len(self.text) >= idx*(steps + 1):
                s = self.text[idx*steps : idx*(steps + 1)]
            else:
                s = self.text[idx*steps : 0]
            
            self.text_bits.append(Text(s, colors[idx], self.styles))

        self.text = ""

        return self


    def hover(self, action: HoverAction, value: Union[str, "Text"]) -> "Text":
        
        self.hover_action = (action, value)
        return self
    

    def click(self, action: ClickAction, value: Union[str, "Text"]) -> "Text":
        
        self.click_action = (action, value)
        return self


def black(text: str) -> Text:
        
    text = Text(text, Color.Black)
    return text


def dark_blue(text: str) -> Text:
    
    text = Text(text, Color.DarkBlue)
    return text


def dark_green(text: str) -> Text:
    
    text = Text(text, Color.DarkGreen)
    return text


def dark_aqua(text: str) -> Text:
    
    text = Text(text, Color.DarkAqua)
    return text


def dark_red(text: str) -> Text:
    
    text = Text(text, Color.DarkRed)
    return text


def dark_purple(text: str) -> Text:
    
    text = Text(text, Color.DarkPurple)
    return text


def gold(text: str) -> Text:
    
    text = Text(text, Color.Gold)
    return text


def gray(text: str) -> Text:
    
    text = Text(text, Color.Gray)
    return text


def dark_gray(text: str) -> Text:
    
    text = Text(text, Color.DarkGray)
    return text


def blue(text: str) -> Text:
    
    text = Text(text, Color.Blue)
    return text


def green(text: str) -> Text:
    
    text = Text(text, Color.Green)
    return text


def aqua(text: str) -> Text:
    
    text = Text(text, Color.Aqua)
    return text


def red(text: str) -> Text:
    
    text = Text(text, Color.Red)
    return text


def ligth_purple(text: str) -> Text:
    
    text = Text(text, Color.LigthPurple)
    return text


def yellow(text: str) -> Text:
    
    text = Text(text, Color.Yellow)
    return text


def white(text: str) -> Text:
    
    text = Text(text, Color.White)
    return text


def obfuscated(text: str) -> Text:
    
    text = Text(text, styles=Style.Obfuscated)
    return text


def bold(text: str) -> Text:
    
    text = Text(text, styles=Style.Bold)
    return text


def strikethrough(text: str) -> Text:
    
    text = Text(text, styles=Style.Strikethrough)
    return text


def underlined(text: str) -> Text:
    
    text = Text(text, styles=Style.Underlined)
    return text


def italic(text: str) -> Text:
    
    text = Text(text, styles=Style.Italic)
    return text