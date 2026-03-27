from typing import Sequence, TypeVar, Any
from abc import ABC, abstractmethod

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.filters import FilterOrBool
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import Completer
from prompt_toolkit.styles import BaseStyle
from prompt_toolkit.validation import Validator
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.layout.containers import AnyContainer, HSplit, VSplit
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.widgets import Dialog, Label, Button, TextArea, Checkbox, ValidationToolbar
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.layout import Layout


_T = TypeVar("_T")


class Input(ABC):
    """
    Abstract class that represents any user input
    """


    def __init__(
        self,
        label_text: AnyFormattedText,
        widget: Any
    ) -> None:

        self.label_text = label_text
        self.widget = widget

    
    @abstractmethod
    def value(self) -> Any:
        """
        Returns the value that this input holds
        """


class TextInput(Input):
    """
    Text input descriptor
    """


    def __init__(
        self,
        label_text: AnyFormattedText = "",
        default_text: str = "",
        password: FilterOrBool = False,
        completer: Completer | None = None,
        validator: Validator | None = None
    ) -> None:

        def accept(buf: Buffer) -> bool:
            return True  # Keep text.

        self._text_area = TextArea(
            text=default_text,
            multiline=False,
            password=password,
            completer=completer,
            validator=validator,
            accept_handler=accept,
            focus_on_click=True,
        )

        super().__init__(label_text, self._text_area)
    
    
    def value(self) -> str:
        return self._text_area.text


class CheckboxInput(Input):
    """
    Checkbox input descriptor
    """


    def __init__(
        self,
        label_text: AnyFormattedText = "",
        checked: bool = False
    ) -> None:
        
        self._check_box = Checkbox(
            text=label_text,
            checked=checked
        )
        self._check_box.window.show_cursor = False # type: ignore

        super().__init__("", self._check_box)

    
    def value(self) -> bool:
        return self._check_box.checked


def multi_input_dialog(
    title: AnyFormattedText,
    inputs: Sequence[Input],
    ok_text: str = "OK",
    cancel_text: str = "Cancel",
    style: BaseStyle | None = None
    ) -> Application[Sequence[Any]]:
    """
    Display multiple input fields with a label on the right.
    Return the given text, or None when cancelled.
    """

    def accept(buf: Buffer) -> bool:
        get_app().layout.focus(ok_button)
        return True  # Keep text.

    def ok_handler() -> None:
        get_app().exit(result=[i.value() for i in inputs])

    ok_button = Button(text=ok_text, handler=ok_handler)
    cancel_button = Button(text=cancel_text, handler=_return_none)

    if inputs is None:
        inputs = []

    values = []
    label_width = max(len(str(i.label_text)) for i in inputs) if inputs else 0

    for input in inputs:

        if isinstance(input, CheckboxInput):
            values.append(input.widget)
            continue
        
        values.append(
            VSplit([
                input.widget,
                Label(text=input.label_text, dont_extend_height=True, width=D(label_width))
            ],padding=D(preferred=1, max=1))
        )

    dialog = Dialog(
        title=title,
        body=HSplit(values + [ValidationToolbar()], padding=D(preferred=1, max=1)),
        buttons=[ok_button, cancel_button],
        with_background=True
    )

    app = _create_app(dialog, style)

    if len(inputs) > 0:
        app.layout.focus(inputs[0].widget)

    return app


# from: https://github.com/prompt-toolkit/python-prompt-toolkit/blob/main/src/prompt_toolkit/shortcuts/dialogs.py
def _create_app(dialog: AnyContainer, style: BaseStyle | None) -> Application[Any]:
    # Key bindings.
    bindings = KeyBindings()
    bindings.add("tab")(focus_next)
    bindings.add("s-tab")(focus_previous)
    bindings.add("up")(focus_previous)
    bindings.add("down")(focus_next)

    return Application(
        layout=Layout(dialog),
        key_bindings=merge_key_bindings([load_key_bindings(), bindings]),
        mouse_support=True,
        style=style,
        full_screen=True,
    )


# from: https://github.com/prompt-toolkit/python-prompt-toolkit/blob/main/src/prompt_toolkit/shortcuts/dialogs.py
def _return_none() -> None:
    "Button handler that returns None."
    get_app().exit()