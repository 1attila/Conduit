from mconduit.text.text import Text
from mconduit.enums.color import Color
from mconduit.text.style import Style


def test_text_from_dict_simple():

    d = {"text": "Simple", "color": "red", "bold": True}
    t = Text.from_dict(d)

    assert t.text == "Simple"
    assert t.color == "red"
    assert Style.BOLD in t.styles


def test_text_from_dict_list_of_elements():

    d_list = [
        {"text": "First", "color": "gold"},
        {"text": " Second", "italic": True}
    ]
    t = Text.from_dict(d_list)

    assert t.plain_text == "First Second"
    assert t.color == "gold"
    assert len(t.text_bits) == 1
    assert Style.ITALIC in t.text_bits[0].styles


def test_text_from_dict_hover_parsing():

    d = {
        "text": "Hover Me",
        "hoverEvent": {
            "action": "show_text",
            "value": "My Tooltip"
        }
    }
    t = Text.from_dict(d)

    assert t.hover_action == ("show_text", "My Tooltip")


# def test_text_from_dict_click_parsing_modern():

#     d = {
#         "text": "Click Me",
#         "click_event": {
#             "action": "suggest_command",
#             "command": "/help"
#         }
#     }
#     t = Text.from_dict(d)
        
#     assert t.click_action == ("suggest_command", "/help")