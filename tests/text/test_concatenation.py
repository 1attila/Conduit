from mconduit.text.text import Text
from mconduit.enums.color import Color
from mconduit.text.style import Style


def test_add_plain_strings():

    t = Text("Hello")
    t = t + " World"

    assert t.text == "Hello World"
    assert len(t.text_bits) == 0


def test_add_formatted_to_plain():

    t1 = Text("Base")
    t2 = Text("Added", Color.RED, Style.BOLD)
    result = t1 + t2

    assert result.text == "Base"
    assert len(result.text_bits) == 1
    assert result.text_bits[0].text == "Added"
    assert result.text_bits[0].color == Color.RED
    assert Style.BOLD in result.text_bits[0].styles


def test_add_plain_to_formatted_appends_correctly():

    t1 = Text("Styled", Color.GREEN, Style.ITALIC)
    result = t1 + " Plain"

    assert result.text == "Styled"
    assert len(result.text_bits) == 1
    assert result.text_bits[0].text == " Plain"
    assert result.text_bits[0].color == Color.GREEN
    assert len(result.text_bits[0].styles) == 0


def test_iadd_operator():

    t = Text("IAdd")
    t += " Success"

    assert t.text == "IAdd Success"


def test_radd_operator_simple():

    t = Text("End")
    result = "Start " + t

    assert result.text == "Start End"
    assert len(result.text_bits) == 0


def test_radd_operator_formatted():

    t = Text("Styled", Color.GOLD, Style.BOLD)
    result = "Plain " + t

    assert result.text == "Plain "
    assert result.color == Color.GOLD
    assert len(result.text_bits) == 1
    assert result.text_bits[0].text == "Styled"
    assert result.text_bits[0].color == Color.GOLD
    assert Style.BOLD in result.text_bits[0].styles


def test_flattened_constraint_assertion():

    t1 = Text("Root")
    t2 = Text("Child1")
    t3 = Text("Child2")
        
    t2 = t2 + t3
    t1 = t1 + t2
        
    assert len(t1.text_bits) == 2
        
    for bit in t1.text_bits:
        assert len(bit.text_bits) == 0