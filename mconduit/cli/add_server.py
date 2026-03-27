from typing import Optional, Callable, Union, List
from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog, yes_no_dialog, progress_dialog
from prompt_toolkit.formatted_text import FormattedText
from pathlib import Path
import asyncio

from .multi_input_dialog import multi_input_dialog, TextInput, CheckboxInput
from .error_dialog import ErrorDialog
from .directory_selector import DirectorySelector
from .version_selector import VersionSelector
from ..utils.version_fetcher import (
    download_server_jar,
    agree_eula,
    fetch_vanilla_url,
    generate_server_properties
)
from .styles import *
from ..lang import Lang
from ..conduit_config import ServerRunnerConfig, RconConfig
from ..config_setup import (
    find_servers,
    generate_rcon_password,
    get_ip_port_mappings,
    get_port
)
from ..server_api import Properties


class RconConfigSetter:

    def __init__(
        self,
        lang: Lang,
        path: Path,
        other_servers_configs: List[ServerRunnerConfig]
    ) -> None:
        
        self.lang = lang
        self.path = path
        self.other_servers_configs = other_servers_configs


    def run(self):

        l = self.lang
        prop = Properties(path=self.path)

        ip = prop.get("server-ip", "127.0.0.1")
        
        if ip == "":
            ip = "127.0.0.1"

        mappings = get_ip_port_mappings(self.other_servers_configs)
        print(mappings)
        safe_server_port = get_port(ip, 25565, mappings=mappings)

        server_port = prop.get("server-port", -1)

        if server_port == -1:
            server_port = safe_server_port

        elif server_port == "" or int(server_port) in mappings.get(ip, []):

            prop.set("server-port", safe_server_port)
            server_port = safe_server_port
        else:
            server_port = int(server_port)

        mappings.setdefault(ip, []).append(server_port)
        
        default_rcon_port = str(get_port(ip, 25575, mappings=mappings))
        port = prop.get("rcon.port", -1)
        
        if port == -1:
            port = default_rcon_port

        elif port == "" or int(port) in mappings[ip]:
            port = default_rcon_port

        password = prop.get("rcon.password", generate_rcon_password())
        
        if password == "":
            password = generate_rcon_password()

        out = multi_input_dialog(
            title=deep_blue(l["Configure server - Rcon configs (2/3)"]),
            inputs=[
                TextInput(
                    deep_blue("Rcon ip"),
                    ip
                ),
                TextInput(
                    deep_blue("Rcon port"),
                    port
                ),
                TextInput(
                    deep_blue("Rcon password"),
                    password,
                    password=True
                )
            ],
            style=welcome_style
        ).run()

        if out is None:
            ErrorDialog(
                l["Rcon configs not set"],
                l["You must press 'ok' to continue!"]
            ).run()
            return

        ip, port, password = out

        config = RconConfig()
        config.address = ip
        config.port = int(port)
        config.password = password

        prop.set("rcon.port", port)
        prop.set("rcon.password", password)
        prop.set("enable-rcon", True)

        return config


class ServerConfigSetter:

    def __init__(
        self,
        lang: Lang,
        path: Path,
        other_servers_configs: Optional[List[ServerRunnerConfig]] = None
    ) -> None:

        self.lang = lang
        self.path = path

        if other_servers_configs is None:
            self.other_servers_configs = []
        else:
            self.other_servers_configs = other_servers_configs


    def run(self):
        
        l = self.lang
        start_command = f"java -Xms1024M -Xmx2048M -jar {self.path / 'server.jar'} --nogui"
        
        out = multi_input_dialog(
            title=deep_blue("Configure server - basic configs (1/3)"),
            inputs=[
                TextInput(
                    deep_blue(l["name(s)"]),
                    self.path.name
                ),
                TextInput(
                    deep_blue(l["start command"]),
                    start_command
                ),
                TextInput(
                    deep_blue(l["lang"]),
                    self.lang.lang
                ),
                CheckboxInput(
                    deep_blue(l["modify server.properties"]),
                    False
                )
            ],
            style=welcome_style
        ).run()

        if out is None:

            ErrorDialog(
                l["Server configs not set"],
                l["You must press 'ok' to continue!"]
            ).run()
            return

        names, start_command, lang, modify = out
        names = names.strip().split(" ")
        names = [name.strip() for name in names if len(name.strip()) > 0]

        config = ServerRunnerConfig()
        config.machine_config = None
        config.path = self.path
        config.start_command = start_command
        config.language = lang
        config.high_permissions = modify
        config.names = names
        config.resource_pack_config = None

        rcon_config = RconConfigSetter(self.lang, self.path, self.other_servers_configs).run()

        if rcon_config is not None:
            
            config.rcon_config = rcon_config
            return config


class Automatic:

    def __init__(self, lang: Lang) -> None:
        self.lang = lang

    def run(self):

        servers_config = []

        for server_path in find_servers():
            #TODO: Add lang
            keep = yes_no_dialog(
                title=deep_blue("Server found"),
                text=FormattedText([(MID_BLUE, "Want to include the server located inside: "), (f"{MID_BLUE} italic", "\\" + server_path.name),  (MID_BLUE, " ?")]),
                style=welcome_style
            ).run()

            if keep is True:
                servers_config.append(
                    ServerConfigSetter(self.lang, server_path, servers_config).run()
                )

        return servers_config


class Manual:

    def __init__(self, lang: Lang) -> None:
        self.lang = lang

    def run(self):

        l = self.lang

        path = input_dialog(
            title=deep_blue(l["Add Server - Input path"]),
            text=mid_blue(l["Input the directory where the Minecraft server is located:"]),
            style=welcome_style,
            default=str(Path.cwd())
        ).run()

        if path is None:
            return

        if not (Path(path) / "server.jar").exists():
            ErrorDialog(
                l["Server not found"],
                str(Path(path) / "server.jar") + " " + l["doesnt exist"]
            ).run()
            return

        return ServerConfigSetter(self.lang, Path(path)).run()
    

class Download:

    def __init__(self, lang: Lang) -> None:
        self.lang = lang

    def run(self):

        l = self.lang

        server_type = radiolist_dialog(
            title=deep_blue(l["Add Server - Choose type (1/3)"]),
            text=mid_blue(l["Select what kind of server you want to download"]),
            values=[
                (0, FormattedText([(f"{DEEP_BLUE} bold", "vanilla")])),
                #(1, FormattedText([(f"{DEEP_BLUE} bold", "fabric")])) #TODO: Add this, bukkit, forge, quilt, neoforge
            ],
            style=welcome_style
        ).run()
        
        url = VersionSelector(self.lang, server_type).run()

        if url is None:

            ErrorDialog(
                l["No URL was found!"],
                l["You have to download the server yourself"]
            ).run()
            return

        dir = DirectorySelector(
            l["Server Download (3/3)"],
            l["Select where you want to download the server"]
        ).run()

        try:
            
            if server_type == 0: # vanilla
                url = fetch_vanilla_url(url)

            download_server_jar(url, dir)

        except Exception as e:

            ErrorDialog(
                title=l["Server download failed!"],
                text=str(e),
            ).run()
            return {} # TODO

        EULA_LINK = "https://www.minecraft.net/en-us/eula"
        
        eula = yes_no_dialog(
            title=deep_blue(l["Server downloaded sucesfully!"]),
            text=mid_blue(f"{l['Do you agree to Minecraft EULA?']}\n{EULA_LINK}"),
            style=welcome_style
        ).run()

        captured_error = []

        if eula is True:
            agree_eula(dir)

            async def run_progress():

                def progress(set_perc: Callable[[int], None], log_text: Callable[[str], None]):

                    set_perc(0)

                    try:
                        i = 0

                        for progress in generate_server_properties(dir):

                            if progress == "Done":
                                break

                            i += 1
                            log_text(progress + "\n")
                            set_perc(i*20)
            
                    except Exception as exc:
                        captured_error.append(exc)

                await progress_dialog(
                    deep_blue("Server Download"),
                    deep_blue("Server bootstrap"),
                    progress,
                    style=welcome_style
                ).run_async()
            
            asyncio.run(run_progress())

            if (Path(dir) / "server.properties").exists():
                return ServerConfigSetter(self.lang, Path(dir)).run()
            else:
                ErrorDialog(
                    l["Problem while starting the server"],
                    str(captured_error[0]) if len(captured_error) > 0 else "Unknown error"
                ).run()
            
        else:
            ErrorDialog(
                l["You didnt accept EULA"],
                l["You must accept EULA to run the server!"]
            ).run()
            return


class AddServer:
    """
    Conduit can add a Minecraft server in 3 ways:

    - User can input it's path
    - Conduit can fetch all of them automatically
    - Conduit can download one
    """


    def __init__(self, lang: Lang) -> None:
        self.lang = lang

    def run(self) -> Union[List[ServerRunnerConfig], ServerRunnerConfig, None]:

        def choice(short: str, desc: str) -> FormattedText:
            return FormattedText([
                (f"{DEEP_BLUE} bold", self.lang[short]),
                (MID_BLUE, self.lang[desc])
            ])

        l = self.lang

        fetch_method = radiolist_dialog(
            title=deep_blue(l["Add Server - Finder method"]),
            text=mid_blue(l["Select how you want to add the server"]),
            values=[
                (0, choice("Automatic", "Scan this machine to find all Minecraft servers")),
                (1, choice("Manual", "Input the directory of the server")),
                (2, choice("Download", "Create a new one"))
            ],
            default=0,
            style=welcome_style
        ).run()

        match fetch_method:

            case 0:
                return Automatic(self.lang).run()
            
            case 1:
                return Manual(self.lang).run()
            
            case 2:
                return Download(self.lang).run()