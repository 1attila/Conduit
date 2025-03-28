from typing import Union, NoReturn, TYPE_CHECKING
import threading

from ..lang.lang import Lang

if TYPE_CHECKING:
    from ..handler import Handler
    from ..server import Server


class Cli:
    """
    Command Line Interface for Conduit
    """

    __handler: "Handler"
    __lang: "Lang"
    __running: bool
    __gui: bool


    def __init__(self, handler: "Handler", lang: "Lang", gui: bool=False) -> NoReturn:

        self.__handler = handler
        self.__lang = lang
        self.__running = True
        self.__gui = gui

        if self.__gui:
            ...

        else:
            console_thread = threading.Thread(target=self.__console_loop_thread, daemon=True)
            console_thread.start()


    def __console_loop_thread(self) -> NoReturn:
        """
        Reads console input in loop on a thread
        """

        try:
            while self.__running:
                try:
                    prompt = input("> ")
                    if prompt:
                        result = self(prompt)
                        if result:
                            print(result)

                except EOFError:
                    break
                
        except KeyboardInterrupt:
            self.__running = False

        finally:
            print("Closing Conduit CLI")


    def __print_help(self) -> str:
        """Help command"""

        return """
        Conduit CLI commands:

        - handler.start-servers
        - handler.stop-servers
        - <server-name>.start
        - <server-name>.stop
        - <server-name>.get-online-players
        - <server-name>.set-language <lang-path>

        You can read servers/handler attributes by doing:
        - <server-name/handler>.<attribute-name>
        Or modify it (if it's allowed) by doing:
        - <server-name/handler>.<attribute-name> = <new-value>
        For more infos go to https://github.com/1attila/Conduit
        """


    def __handle_attributes(self, command: str, obj: Union["Handler", "Server"]) -> bool:
        """
        Tries to read/edit an attribute
        """

        if "=" in command:
            attr, value = command.split("=")
            attr = attr[:-1].strip()
            value = value.strip()
            
            if hasattr(obj, attr):
                
                setattr(obj, attr, value)
                Set = self.__lang["Set"]

                if hasattr(obj, "name"):
                    print(f"{Set} {obj.name}.{attr} = {value}")
                else:
                    print(f"{Set} {obj.__str__()}.{attr} = {value}")

                return True

        elif hasattr(obj, command):

            print(getattr(obj, command))

            return True
        
        return False


    def __call__(self, prompt: str) -> str:
        """
        Cli commands

        syntaxt:
        <handler/server-name> <command/attribute>

        Example: smp.online_players
        """

        prompt = prompt.strip()

        if prompt == "":
            return ""
        
        if prompt in ("help", "?"):
            return self.__print_help()

        if prompt.startswith("handler"):
            command = prompt[8:]

            if self.__handle_attributes(command, self.__handler):
                return ""
            
            handler_commands = {
                "start-servers": self.__handler.start_servers,
                "stop-servers": self.__handler.stop_servers,
            }

            if command in handler_commands:
                handler_commands[command]()
                return ""

            elif command.startswith("set-language"):

                command = command[13:]
                self.__handler.set_lang(command.strip())

                
                return self.__lang["Language is now set to"].join(command.strip())
            
            self.__handler.to_all_servers(lambda s: s.execute(command))

        else:
            for server in self.__handler.servers:
                for name in server.names:

                    if prompt.startswith(name):
                        
                        command = prompt[len(name)+1:]

                        if self.__handle_attributes(command, server):
                            return ""
                        
                        server_commands = {
                            "start": server.start,
                            "stop": server.stop,
                            "get-online-players": lambda: (
                                str([p._name for p in server.get_online_players()]) or "[]"
                            )
                        }

                        if command in server_commands:
                            server_commands[command]()
                            return ""

                        elif command.startswith("set-language"):
                            command = command[13:]
                            server.set_lang(command.strip())

                            return server.name, self.__lang["Language is now set to"].join(command.strip())
                        
                        server.execute(command)

                        return ""