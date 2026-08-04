from prompt_toolkit.shortcuts import radiolist_dialog
from pathlib import Path

from mconduit.cli.error_dialog import ErrorDialog
from mconduit.cli.styles import *
from mconduit.lang import Lang


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
                "Unable to load lang file",
                "The selected language file may be corrupted, contact the author of this program"
            ).run()
            raise

        lang.set_lang(selected_lang)
        
        return lang