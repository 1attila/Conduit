from mconduit.text.text import Text
from mconduit.enums.color import Color
from mconduit.text.style import Style


def test_color_chains():

    t = Text("Multi") + " Colored"
    t.gold()

    assert t.color == Color.GOLD

    for bit in t.text_bits:
        assert bit.color == Color.GOLD


def test_style_operations():

    t = Text("Styled").bold().italic().underlined().strikethrough().obfuscated()

    assert Style.BOLD in t.styles
    assert Style.ITALIC in t.styles
    assert Style.UNDERLINED in t.styles
    assert Style.STRIKETHROUGH in t.styles
    assert Style.OBFUSCATED in t.styles