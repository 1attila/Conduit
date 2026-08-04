from mconduit.text.text import Text, link, button, suggester, quoted


def test_text_link():

    url = "https://minecraft.net"
    lnk = link(url, "Minecraft Site")

    assert lnk.text == "Minecraft Site"
    assert "underlined" in [s.value for s in lnk.styles]
    assert lnk.hover_action == ("show_text", "Click to open")
    assert lnk.click_action == ("open_url", url)


def test_text_button():

    btn = button("Click Me", run_command="/say hi")

    assert btn.text == "[Click Me]"
    assert "underlined" in [s.value for s in btn.styles]
    assert btn.click_action == ("run_command", "/say hi")


def test_button_with_function_and_sound():

    executed = False
    def fake_callback(context):
        nonlocal executed
        executed = True

    class MockServer:
        def execute(self, cmd):
            pass
        
    class MockContext:
        def __init__(self):
            self.server = MockServer()
            self.player = "Steve"

    btn = button("Play", sound="ui.button.click", run_function=fake_callback)
    assert btn.click_action[0] == "run_function"
        
    ctx = MockContext()
    btn.click_action[1](ctx)
    assert executed is True


def test_text_suggester():

    sug = suggester("warp", "creative", prefix="/")

    assert sug.plain_text == "/ warp creative"
    
    warp_bit = sug.text_bits[0]
    assert warp_bit.click_action == ("suggest_command", "/warp")
        
    creative_bit = sug.text_bits[2]
    assert creative_bit.click_action == ("suggest_command", "/warp creative")


def test_quoted_text():

    assert quoted("hello") == "`hello`"
        
    t = Text("styled")
    quoted_t = quoted(t)
    assert quoted_t.text == "`styled`"