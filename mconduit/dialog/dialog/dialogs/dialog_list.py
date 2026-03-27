from typing import List

from .base_dialog import BaseDialog
from .body_format import BodyFormat
from ..json import Field


class DialogList(BaseDialog):
    """
    Docstring for DialogList
    """

    dialogs: Field[List[BaseDialog]]
    exit_action: Field[None] #TODO: Implement
    columns: Field[int, None, 2]
    button_width: Field[int, None, 150]


    def __init__(
        self,
        title: Message,
        external_title: str | None = None,
        body: List[BodyFormat] | None = None,
        inputs: List[BaseInput] | None = None,
        can_close_with_escape: bool = True,
        pause: bool = True,
        after_action: AfterAction = AfterAction.Close,
        *,
        dialogs: List[BaseDialog],
        exit_action: None,
        columns: int = 2,
        button_width: int = 150
    ) -> "DialogList":
        
        super().__init__(
            type=DialogType.Confirmation,
            title=title,
            external_title=external_title,
            body=body,
            inputs=inputs,
            can_close_with_escape=can_close_with_escape,
            pause=pause,
            after_action=after_action
        )
        raise NotImplementedError("Exit action!!")

        self.dialogs = dialogs
        self.columns = columns
        #TODO: Exit action
        self.button_width = button_width