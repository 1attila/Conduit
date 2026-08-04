from typing import Optional
from prompt_toolkit.shortcuts import radiolist_dialog, yes_no_dialog

from mconduit.cli.styles import *
from mconduit.cli.error_dialog import ErrorDialog
from mconduit.lang import Lang
from mconduit.utils import fetch_vanilla_versions, fetch_fabric_versions


class VersionSelector:

    def __init__(self, lang: Lang, type: int) -> None:
        self.lang = lang
        self.type = type

    def run(self) -> Optional[str]:

        l = self.lang
            
        snapshots = yes_no_dialog(
            title=deep_blue(l["Server Download - Choose snapshots (1.1/3)"]),
            text=mid_blue(l["Do you want to install a snapshot?"]),
            style=welcome_style
        ).run()

        if self.type == 0: # vanilla
            versions = fetch_vanilla_versions(snapshots, True)

        elif self.type == 1: # fabric
            versions = fetch_fabric_versions(snapshots, True)
        
        values = [(v, deep_blue(k)) for k, v in versions.items()] # type: ignore

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

            return None