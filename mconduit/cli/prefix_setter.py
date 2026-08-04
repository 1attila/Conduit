from prompt_toolkit.shortcuts import input_dialog

from mconduit.cli.error_dialog import ErrorDialog
from mconduit.cli.styles import *
from mconduit.lang import Lang


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

        if prefix is None or len(prefix.strip()) == 0:
            ErrorDialog(
                "Invalid command prefix",
                "It must be a non-space character"
            ).run()
            raise

        return prefix.strip()