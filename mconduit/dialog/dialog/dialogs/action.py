from typing import Dict

from .base_dialog import BaseDialog
from ..to_json import to_json
from ..json import Serializable, Field


class Action(Serializable):
    """
    Base action class.
    """


    _type: Field[str, "type"]


    def __init__(
        self,
        type: str
    ) -> None:
        self._type = type


class OpenUrl(Action):


    url: Field[str]


    def __init__(
        self,
        url: str
    ) -> None:

        super().__init__("open_url")
        self.url = url


class RunCommand(Action):


    command: Field[str]


    def __init__(
        self,
        command: str
    ) -> None:

        super().__init__("run_command")
        self.command = command


class SuggestCommand(Action):


    command: Field[str]


    def __init__(
        self,
        command: str
    ) -> None:

        super().__init__("suggest_command")
        self.command = command


class ChangePage(Action):


    page: Field[int]


    def __init__(
        self,
        page: int
    ) -> None:

        super().__init__("change_page")
        self.page = page

    
class CopyToClipboard(Action):


    value: Field[str]


    def __init__(
        self,
        value: str
    ) -> None:

        super().__init__("copy_to_clipboard")
        self.value = value


class ShowDialog(Action):


    dialog: Field[BaseDialog]


    def __init__(
        self,
        dialog: BaseDialog
    ) -> None:

        super().__init__("show_dialog")
        self.dialog = dialog


class Custom(Action):


    id: Field[str]
    payload: Field[str]


    def __init__(
        self,
        id: str,
        payload: str
    ) -> None:

        super().__init__("custom")
        self.id = id
        self.payload = payload


class DynamicRunCommand(Action):


    template: Field[str]


    def __init__(
        self,
        template: str
    ) -> None:

        super().__init__("dynamic/run_command")
        self.template = template

    
class DynamicCustom(Action):


    additions: Field[Dict]
    id: Field[str]


    def __init__(
        self,
        additions: Dict,
        id: str
    ) -> None:

        super().__init__("dynamic/custom")
        self.additions = additions
        self.id = id