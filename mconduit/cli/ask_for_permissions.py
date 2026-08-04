from typing import List, TYPE_CHECKING
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit import prompt

from mconduit.cli.non_repeating_word_completer import NonRepeatingWordCompleter
from mconduit.cli.styles import *

if TYPE_CHECKING:
    from mconduit.server import Server


class SetPermission:
    """
    Sets a specific permission
    """


    def __init__(
        self,
        server: "Server",
        all_players: List[str],
        perm: str
    ) -> None:
        
        self.server = server
        self.all_players = all_players
        self.perm = perm

    
    def run(self) -> None:

        l = self.server.lang
        
        completer = NonRepeatingWordCompleter(self.all_players, ignore_case=True)

        players = prompt(
            l[f"Enter players for {self.perm.upper()} (press ENTER to skip) > "],
            completer=completer,
            complete_while_typing=True
        )
        
        for player in players.strip().split(" "):

            player = player.replace(" ", "")

            try:
                self.all_players.remove(player)
            except ValueError:
                pass

            if len(player) > 0:
                self.server.permission_manager.add_perm(player, self.perm)


class AskForPermissions:
    """
    Asks to set the server permissions
    """


    def __init__(
        self,
        server: "Server",
    ) -> None:
        
        self.server = server

    
    def run(self) -> None:

        l = self.server.handler.lang

        text = FormattedText([
            (MID_BLUE,            l[f"You didnt set higher permissions for {self.server}!"] + "\n\n"),
            (MID_BLUE,            l[f"This is what each permission allows"] + ":\n"),
            (DEEP_BLUE + " bold", " • "),
            (GRAY + " bold",      "Guest"),
            (MID_BLUE,            ":  " + l["help and infos"] + "\n"),
            (DEEP_BLUE + " bold", " • "),
            (AQUA + " bold",      "Helper"),
            (MID_BLUE,            ": " + l["plugin manipulation"] + "\n"),
            (DEEP_BLUE + " bold", " • "),
            (DARK_AQUA + " bold", "Admin"),
            (MID_BLUE,            ":  " + l["permission manipulation"] + "\n")
        ])
        
        set_permissions = yes_no_dialog(
            title=bold_deep_blue(l["Missing server permissions"]),
            text=text
        ).run()
        
        if set_permissions is True:
            
            perms = ["guest", "user", "helper", "admin", "owner"]

            all_players = self.server.get_all_joined_players()

            for perm in perms:

                SetPermission(
                    self.server,
                    all_players,
                    perm
                ).run()