from prompt_toolkit.shortcuts import input_dialog

from .error_dialog import ErrorDialog
from ..lang import Lang
from .styles import *


class PrefixSetter:
    """
    Asks for the command prefix to use in Minecraft.

    Default: !!
    """


    def __init__(self, lang: Lang) -> None:
        self.lang = lang


    def run(self) -> str:

        l = self.lang

        prefix = input_dialog(
            title=deep_blue(l["Global Configuration (2/2)"]),
            text=mid_blue(l["Select the command prefix you want to use in Minecraft:"]),
            default="!!",
            style=welcome_style
        ).run()

        if prefix is None:
            ErrorDialog(

            ).run()
            raise

        return prefix