from typing import List

from mconduit import Message
from ..json import Field

from .dialog_type import DialogType
from .base_dialog import BaseDialog
from .body_format import BodyFormat
from .action import Action
from ..after_action import AfterAction
from ..input.base_input import BaseInput
from ..to_json import to_json


class Confirmation(BaseDialog):
    """
    
    """

    yes: Field[Action]
    no: Field[Action]


    def __init__(
        self,
        title: Message,
        external_title: str | None = None,
        body: List[BodyFormat] | None = None,
        inputs: List[BaseInput] | None = None,
        can_close_with_escape: bool = True,
        pause: bool = True,
        after_action: AfterAction = AfterAction.CLOSE,
        *,
        yes: Action,
        no: Action
    ) -> None:
        
        super().__init__(
            type=DialogType.CONFIRMATION,
            title=title,
            external_title=external_title,
            body=body,
            inputs=inputs,
            can_close_with_escape=can_close_with_escape,
            pause=pause,
            after_action=after_action
        )

        self.yes = yes
        self.no = no


    def to_dict(self):
        
        return super().to_dict() + {
            "yes": self.yes.to_json(),
            "no": self.no.to_json()
        }