from typing import Union
import copy

from mconduit.text.text import Text
from mconduit.enums.color import Color


def default_color(color: Color) -> "TextWithDefaultColor":

    class TextWithDefaultColor(Text):

        def __radd__(self: Text, other: str) -> "Text":

            inst = copy.deepcopy(self)

            if len(inst.styles) == 0 and inst.color == color:
                inst.text = str(other) + inst.text
        
            else:
                inst.text_bits.insert(0, Text(other, color))

            return inst
        
    
        def __add__(self: Text, text: Union["Text", str]) -> "Text":
        
            inst = copy.deepcopy(self)

            if type(text) is Text:
                return inst(text)
            else:

                if len(inst.text_bits) > 0:
                
                    tb = inst.text_bits[-1]

                    if len(tb.styles) == 0 and tb.hover_action == () and tb.click_action == () and tb.color == color:
                        tb.text += text
                        return inst

                elif len(inst.styles) == 0 and inst.hover_action == () and inst.hover_action == () and inst.color == color:
                    inst.text += text
                    return inst
            
                return inst(Text(text, color))
            
    return TextWithDefaultColor