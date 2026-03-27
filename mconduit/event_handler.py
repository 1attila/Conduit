from typing import Optional, Union, Callable, List, TYPE_CHECKING

from .event import Event, EventListener
from .context import Context
from .stdout_parser import ParsedResult

if TYPE_CHECKING:
    from .server import Server


class EventHandler:
    """
    Handles and dispatch events
    """


    __listeners: List[Union[EventListener, Event]]
    __server: "Server"


    def __init__(self, server: "Server") -> None:

        self.__server = server
        self.__listeners = []
        # TODO: Add the async listeners EXACTLY HERE
        self.__server._on_conduit_start()


    def process_parsed_stdout(self, parsed: ParsedResult) -> Context:
        
        match parsed.event:
            
            case Event.PlayerJoin:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerJoin)
            case Event.PlayerLeft:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerLeft)
            case Event.PlayerDeath:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerDeath, message=parsed.infos["msg"])
            case Event.PlayerChat:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerChat, message=parsed.infos["msg"])
            case Event.PlayerCommand:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerCommand, message=parsed.infos["cmd"])
            case Event.PlayerWhitelisted:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerWhitelisted, other_player=parsed.infos["other_player"])
            case Event.PlayerUnwhitelisted:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerUnwhitelisted, other_player=parsed.infos["other_player"])
            case Event.PlayerOpped:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerOpped, other_player=parsed.infos["other_player"])
            case Event.PlayerDeopped:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerDeopped, other_player=parsed.infos["other_player"])
            case Event.PlayerKicked:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerKicked, other_player=parsed.infos["other_player"])
            case Event.PlayerAdvancement:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerAdvancement, advancement=parsed.infos["advancement"])
            case Event.PlayerChallenge:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerChallenge, advancement=parsed.infos["challenge"])
            case Event.PlayerTrigger:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerTrigger, trigger=parsed.infos["trigger"])
            case Event.SetScoreboardValue:
                return Context(parsed.player, parsed.time, parsed.server, Event.SetScoreboardValue, other_player=parsed.infos["other_player"], scoreboard=parsed.infos["scoreboard"], value=parsed.infos["value"])
            case Event.AddScoreboardValue:
                return Context(parsed.player, parsed.time, parsed.server, Event.AddScoreboardValue, other_player=parsed.infos["other_player"], scoreboard=parsed.infos["scoreboard"], value=parsed.infos["value"], amount=parsed.infos["amount"])
            case Event.SubScoreboardValue:
                return Context(parsed.player, parsed.time, parsed.server, Event.SubScoreboardValue, other_player=parsed.infos["other_player"], scoreboard=parsed.infos["scoreboard"], value=parsed.infos["value"], amount=parsed.infos["amount"])
            case Event.ResetScoreboardValue:
                return Context(parsed.player, parsed.time, parsed.server, Event.ResetScoreboardValue, other_player=parsed.infos["other_player"], scoreboard=parsed.infos["scoreboard"])
            case Event.ServerStart:
                return Context(parsed.player, parsed.time, parsed.server, Event.ServerStart)
            case Event.ServerStop:
                return Context(parsed.player, parsed.time, parsed.server, Event.ServerStop)


    def __call__(
        self,
        player_event: Optional[ParsedResult] = None
    ) -> None:
        """
        Dispatch all the events registered for that server.

        Events registered for plugins are stored differently compared to events registered from the server
        """

        if player_event is not None:

            if player_event.event == Event.PlayerTrigger:
                
                trigger_name = player_event.infos["trigger"]

                self.__server.execute(f"/scoreboard players enable @e {trigger_name}")

                if trigger_name.startswith("mconduit-text-"):
                    self.__server._text_handler.on_player_trigger(player_event)

            ctx: Context = None # Built once only when needed
            server_slots = self.__server.slots
            
            if player_event.event in server_slots.keys():
                ctx = self.process_parsed_stdout(player_event)
                self.__server._on_player_event(ctx)

            for plugin in self.__server.plugin_manager.plugins:
                
                if player_event.event not in plugin.events.keys():
                    continue
                
                for callback in plugin.events[player_event.event]:
                    
                    try:
                        if ctx is None:
                            ctx = self.process_parsed_stdout(player_event)

                        callback(ctx)
                    except:
                        ...
                        

    def dispatch_log_events(self, line: str) -> None:
        """
        Called at every line to dispatch the log events
        """

        for plugin in self.__server.plugin_manager.plugins:

            if Event.OnLog not in plugin.events.keys():
                continue

            for callback in plugin.events[Event.OnLog]:
                try:
                    callback(line)
                except:
                    ...


    def fetch_other_events(self) -> None:
        """
        Fetches and dispatch events that aren't enabled by default
        """

        # Tick all the EventListeners
        """
        ```
        How Hyper Fancy Text should work:

        def hello(ctx: Context):
            ctx.reply("Hello from Python")

        Server.tellraw(text.Text("").click(run_function=hello))

        Server.tellraw(text):

        if text is type(Text) and click_exe:

            scoreboard = Server.generate_new_scoreboard()
            text.click(run_command="scoreboard")
            def check_score(fn):
                if scoreboard:
                    fn()
            server.event_listeners.add(check_score)
        ```
        """
        
        for listener in self.__listeners:
            self.__process_listener(listener)

        for plugin in self.__server.plugin_manager.plugins:
            ...


    def __process_listener(self, listener: Union[Event, EventListener]) -> None:
        """
        Run every listener or event separately
        """
        
        if issubclass(listener.__class__, EventListener):
            
            if listener.enabled is True:
                try:
                    listener.tick()
                except:
                    pass

            if hasattr(listener, "__detach_flag"):
                if getattr(listener, "__detach_flag") is True:
                    self.__listeners.remove(listener)


    def add_listener(self, listener: EventListener, *functions: List[Callable]) -> None:
        """
        Adds the given listener to the slots
        """

        self.__listeners.append(listener)

        for f in functions:
            listener.add_fallback(f)
    
    
    # This function it's quite outdated, will be removed soon
    # In the meantime, a `_` has been added to it's name to avoid confusion
    # I know, it's bad
    def _add_listener(self, event: Event, fn: Callable) -> None:
        """
        The function that gets called by the event must have only a single parameter of type Context
        """

        assert event not in [
            Event.PlayerLeftClick,
            Event.PlayerRigthClick,
            Event.PlayerShift
        ], "This event is registered by default"

        annotation = fn.__annotations__

        if "return" in annotation.keys():
            annotation.pop("return")

        for item in annotation.values():
            param = item
        
        if type(param) == Context:
            self.__listeners.setdefault(event, []).append(fn)