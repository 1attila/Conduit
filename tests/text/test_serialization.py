from mconduit.text.text import Text
from mconduit.enums.color import Color
from mconduit.text.style import Style


def test_to_json_legacy_format():

    t = Text("Hello", Color.RED, Style.BOLD)
    t.hover(show_text="Hover text")
    t.click(run_command="/command")

    serialized = t.to_json(use_v1215_format=False)

    assert serialized["text"] == "Hello"
    assert serialized["color"] == "red"
    assert serialized["bold"] is True
    assert serialized["hoverEvent"]["action"] == "show_text"
    assert serialized["hoverEvent"]["value"] == "Hover text"
    assert serialized["clickEvent"]["action"] == "run_command"
    assert serialized["clickEvent"]["value"] == "/command"


def test_to_json_modern_v1_21_5_format():

    t = Text("Modern", Color.BLUE, Style.ITALIC)
    t.hover(show_entity="UUID-1234")
    t.click(open_url="https://mojang.com")

    serialized = t.to_json(use_v1215_format=True)

    assert serialized["text"] == "Modern"
    assert serialized["color"] == "blue"
    assert serialized["italic"] is True
    assert serialized["hover_event"]["action"] == "show_entity"
    assert serialized["hover_event"]["contents"] == "UUID-1234"
    assert serialized["click_event"]["action"] == "open_url"
    assert serialized["click_event"]["url"] == "https://mojang.com"


def test_serialization_no_mutation_side_effect():

    t = Text("Text") + " Bit"
    t.hover(show_text="Hover")
        
    len_before = len(t.text_bits)
    t.to_json(use_v1215_format=False)
    len_after = len(t.text_bits)
        
    assert len_before == len_after