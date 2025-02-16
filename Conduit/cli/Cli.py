from typing import Union, NoReturn, TYPE_CHECKING
import threading

from Conduit.Lang.Lang import Lang 

if TYPE_CHECKING:
    from Conduit.Handler import Handler
    from Conduit.Server import Server
    from Conduit.Lang.Lang import Lang


class Cli:
    """
    Command Line Interface for Conduit
    """

    __handler: "Handler"
    __lang: "Lang"


    def __init__(self, handler: "Handler", lang: "Lang") -> NoReturn:

        self.__handler = handler
        self.__lang = lang
        console_thread = threading.Thread(target=self.__console_loop_thread)
        console_thread.start()


    def __console_loop_thread(self) -> NoReturn:
        """
        Reads console input in loop on a thread
        """

        while True:
            self(input("> ") or "")


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


    def __call__(self, prompt: str) -> NoReturn:
        """
        Cli commands

        syntaxt:
        <handler/server-name> <command/attribute>

        Example: smp.online_players
        """

        prompt = prompt.strip()

        if prompt == "":
            return

        if prompt.startswith("handler"):
            command = prompt[8:]

            if self.__handle_attributes(command, self.__handler):
                return
            
            elif command == "start-servers":
                self.__handler.start_servers()

            elif command == "stop-servers":
                self.__handler.stop_servers()

            elif command.startswith("set-language"):

                command = command[13:]
                self.__handler.set_lang(command.strip())

                print(self.__lang["Language is now set to"], command.strip())

            else:
                self.__handler.to_all_servers(lambda s: s.execute(command))

        else:
            for server in self.__handler.servers:
                for name in server.names:

                    if prompt.startswith(name):
                        
                        command = prompt[len(name)+1:]

                        if self.__handle_attributes(command, server):
                            return
                        elif command == "start":
                            server.start()
                        elif command == "stop":
                            server.stop()
                        elif command == "get-online-players":

                            players = server.get_online_players()

                            if players:
                                players = [player._name for player in players]
                            else:
                                players = "[]"
                                    
                            print(players)

                        elif command.startswith("set-language"):
                            command = command[13:]
                            server.set_lang(command.strip())

                            print(server.name, self.__lang["Language is now set to"], command.strip())
                        else:
                            server.execute(command)

                        return