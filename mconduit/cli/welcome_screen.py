from typing import Optional, TYPE_CHECKING
import subprocess
import sys
import os

from prompt_toolkit import Application
from prompt_toolkit.filters import is_done
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import print_formatted_text, prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import Label, Button, Box, Shadow, Frame
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window, Float, FloatContainer

from mconduit.conduit_config import HandlerConfig
from mconduit.cli.setup_wizard import SetupWizard
from mconduit.cli.logo import get_logo
from mconduit.cli.styles import *

if TYPE_CHECKING:
    from mconduit.handler import Handler


class SelectDirectory:

    def run(self):

        print_formatted_text(HTML(f"Current path: <style fg='{MID_BLUE}'>{os.getcwd()}</style>"))

        return prompt(
            mid_blue("New directory"),
            default=os.getcwd(),
            completer=PathCompleter(only_directories=True, expanduser=True),
            show_frame=~is_done,
            style=select_path_style
        )
    

class WelcomeScreen:
    """
    Text user interface invoked when the config.json file is not found.

    This means it's the first time Conduit is launched (in this directory, at least)

    So the user has to choose about what to do:

    - 1 First launch -> setup wizard
    - 2 Wrong directory -> choose the rigth one so conduit can boot automatically
    - 3 Program opened inadvertently -> close
    """


    def __init__(
        self,
        gui:bool,
        update: bool,
        handler: "Handler"
    ) -> None:

        self.gui = gui
        self.update = update
        self.handler = handler


    def _launch_from_path(self, path: str):
        
        args = [sys.executable, "-m", "mconduit", "--restart"]

        if self.gui:
            args.append("--gui")

        if self.update:
            args.append("--update")

        sys.stdout.flush()

        os.chdir(path)
        subprocess.run(args)

        sys.exit()


    def run(self):

        kb = KeyBindings()

        def exit_app():
            sys.exit(0)

        def result_setup():
            app.exit(result=1)

        def result_wrong_dir():
            app.exit(result=2)

        logo_label = Label(
            text=get_logo(),
            dont_extend_height=True
        )

        welcome_text = Label(
            text=HTML(
                f"\nWelcome to <style fg='{DEEP_BLUE}'><b>Conduit</b></style>.\n"
                "The configuration file was not found.\n"
                "Let's set up your environment."
            ),
            dont_extend_height=True,
            style="class:dialog-body"
        )

        btn_setup = Button(text="Run Setup Wizard", handler=result_setup, width=25, left_symbol="", right_symbol="")
        btn_dir   = Button(text="Switch Directory", handler=result_wrong_dir, width=25, left_symbol="", right_symbol="")
        btn_exit  = Button(text="Exit", handler=exit_app, width=25, left_symbol="", right_symbol="")

        @kb.add("down")
        def _(event):
            event.app.layout.focus_next()

        @kb.add("up")
        def _(event):
            event.app.layout.focus_previous()

        body_content = HSplit([
            Box(logo_label, padding_bottom=1),
            
            Label(text=deep_blue('—' * 46), dont_extend_height=True),
            
            Box(welcome_text, padding_top=1, padding_bottom=1),
            
            Box(btn_setup, padding_left=10, padding_right=10),
            Box(btn_dir, padding_left=10, padding_right=10),
            Box(btn_exit, padding_left=10, padding_right=10),

            Box(Label(deep_blue(f"v{self.handler.version}"), dont_extend_height=True), padding_left=38)
            
        ], padding=1, align="CENTER", style="class:dialog-body")

        main_window = Box(
            body=Shadow(
                body=Frame(
                    body=body_content,
                    style="class:frame.border"
                )
            ),
            padding=0,
        )

        root_container = FloatContainer(
            content=Window(style=f"bg:{DARK_BG}"),
            floats=[Float(content=main_window)]
        )

        layout = Layout(root_container, focused_element=btn_setup)

        global app
        app = Application(
            layout=layout,
            key_bindings=kb,
            style=welcome_style,
            full_screen=True,
            mouse_support=True
        )

        return self._handle_action(app.run())

    
    def _handle_action(self, action: int) -> Optional[HandlerConfig]:
        
        match action:

            case 1:
                return SetupWizard(self.handler).run()

            case 2:
                path = SelectDirectory().run()
                self._launch_from_path(path)

            case _:
                sys.exit(0)

        return None