from typing import List, Optional

from mconduit import Message

from .base_dialog import BaseDialog
from .dialog_type import DialogType
from .action import Action
from ..after_action import AfterAction
from ..input.base_input import BaseInput
from ..to_json import to_json


class Notice(BaseDialog):
    """

    """

    action: Optional[Action]


    def __init__(
        self,
        title: Message,
        external_title: Optional[str]=None,
        body: Optional[List]=None,
        inputs: Optional[List[BaseInput]]=None,
        can_close_with_escape: bool=True,
        pause: bool=True,
        after_action: AfterAction=AfterAction.NONE,
        *,
        action: Optional[Action]=None
    ) -> "Notice":
        
        super().__init__(
            type=DialogType.Notice,
            title=title,
            external_title=external_title,
            body=body,
            inputs=inputs,
            can_close_with_escape=can_close_with_escape,
            pause=pause,
            after_action=after_action
        )

        self.action = action

    
    def to_dict(self):
        return super().to_dict() + to_json({"action": self.action.to_json()})