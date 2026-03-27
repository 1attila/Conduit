from prompt_toolkit.shortcuts import radiolist_dialog
from pathlib import Path

from .error_dialog import ErrorDialog
from .styles import *
from ..lang import Lang


class LanguageSelector:

    def run(self) -> Lang:

        lang = Lang(Path.cwd() / "resources", "en_us")
        
        values = [(lang, deep_blue(lang)) for lang in lang.avaiable_langs]
        
        selected_lang = radiolist_dialog(
            title=deep_blue("Global Configuration (1/2)"),
            text=mid_blue("Select the default language for Conduit:"),
            values=values,
            default="en_us",
            style=welcome_style
        ).run()

        if selected_lang is None:
            ErrorDialog(

            ).run()
            raise

        lang.set_lang(selected_lang)
        
        return lang