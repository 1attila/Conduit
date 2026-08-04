import warnings
from mconduit.text.text import Text
from mconduit.enums.color import Color
from mconduit.text.style import Style


def test_init_string():

    t = Text("Initial", Color.BLUE, Style.BOLD)

    assert t.text == "Initial"
    assert t.color == Color.BLUE
    assert Style.BOLD in t.styles


def test_init_nested_text_copy():

    original = Text("Original", Color.GOLD, Style.ITALIC)
    copied = Text(original)

    assert copied.text == "Original"
    assert copied.color == Color.GOLD
    assert Style.ITALIC in copied.styles


def test_quote_replacement_and_warnings():

    with warnings.catch_warnings(record=True) as w:
            
        warnings.simplefilter("always")
        t = Text('Contains "quotes" and \'single\'')

        assert t.text == "Contains `quotes` and `single`"
        assert any("quotes" in str(warning.message) for warning in w) is True