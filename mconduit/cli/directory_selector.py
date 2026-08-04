from prompt_toolkit.shortcuts import input_dialog
import os

from mconduit.cli.styles import *



class DirectorySelector:

    def __init__(self, title: str, text: str) -> None:
        self.title = title
        self.text = text
    

    def run(self):

        return input_dialog(
            title=deep_blue(self.title),
            text=mid_blue(self.text),
            default=os.getcwd(),
            style=welcome_style
        ).run()