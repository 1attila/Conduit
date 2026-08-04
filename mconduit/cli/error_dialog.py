from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.shortcuts import message_dialog

from mconduit.cli.styles import *


class ErrorDialog:

    def __init__(
        self,
        title: str,
        text: str
    ) -> None:
        self.title = title
        self.text = text

    def run(self):

        return message_dialog(
            title=FormattedText([(f"{ERROR_RED} bold", self.title)]),
            text=error_red(self.text),
            style=welcome_style
        ).run()