from typing import Optional

from mconduit.text.text import Text


class PermissionItem:
    """
    Holds permission name and value
    """

    name: str
    display_text: Text


    def __init__(
        self,
        name: str,
        display_text: Optional[Text] = None
    ) -> None:

        self.name = name

        if display_text is not None:
            self.display_text = display_text
        else:
            self.display_text = Text(name)


def perm_item(
    name: str,
    display: Optional[Text] = None
) -> PermissionItem:
    """
    Creates a permission item.

    It holds its value and display infos
    """

    return PermissionItem(name, display)