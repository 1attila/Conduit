from prompt_toolkit.shortcuts import radiolist_dialog, yes_no_dialog

from .styles import *
from .error_dialog import ErrorDialog
from ..lang import Lang
from ..utils.version_fetcher import fetch_vanilla_versions


class VersionSelector:

    def __init__(self, lang: Lang, type: int) -> None:
        self.lang = lang
        self.type = type

    def run(self) -> str:

        l = self.lang
        
        if self.type == 0:
            
            snapshots = yes_no_dialog(
                title=deep_blue(l["Server Download - Choose snapshots (1.1/3)"]),
                text=mid_blue(l["Do you want to install a snapshot?"]),
                style=welcome_style
            ).run()

            versions = fetch_vanilla_versions(snapshots, True)
            values = [(v, deep_blue(k)) for k, v in versions.items()]
        else:
            values = []

        if len(values) > 0:
        
            return radiolist_dialog(
                title=deep_blue(l["Server Download (2/3)"]),
                text=mid_blue(l["Select the version of the server:"]),
                values=values,
                style=welcome_style
            ).run()
        
        else:
            ErrorDialog(
                title=l["No version found!"],
                text=l["You must create the server manually!"]
            ).run()