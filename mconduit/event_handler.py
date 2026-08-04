from __future__ import annotations
from typing import Optional, Union, Callable, List, TYPE_CHECKING
import traceback
import copy

from mconduit.event import Event, EventListener
from mconduit.context import Context
from mconduit.stdout_parser import ParsedResult, PLAYER_NOT_SUPPORTED

if TYPE_CHECKING:
    from mconduit.server import Server


class EventHandler:
    """
    Handles and dispatch events
    """


    _listeners: List[Union[EventListener, Event]]
    _server: Server


    def __init__(self, server: Server) -> None:

        self._server = server
        self._listeners = []
        # TODO: Add the async listeners EXACTLY HERE
        self._server._on_conduit_start()


    def process_parsed_stdout(self, parsed: ParsedResult) -> Context:
        
        return Context(parsed.player, parsed.time, parsed.server, parsed.event, **parsed.infos)


    def __call__(
        self,
        player_event: Optional[ParsedResult] = None
    ) -> None:
        """
        Dispatch all the events registered for that server.

        Events registered for plugins are stored differently compared to events registered from the server
        """

        if player_event is not None:

            if player_event.event == Event.PLAYER_TRIGGER:
                
                trigger_name: str = player_event.infos["message"]

                self._server.execute(f"/scoreboard players enable @e {trigger_name}")

                if trigger_name.startswith("mconduit-text-"):
                    self._server._text_handler.on_player_trigger(player_event)

            ctx: Optional[Context] = None # Built once only when needed
            server_slots = self._server.slots
            
            if player_event.event in server_slots.keys():
                ctx = self.process_parsed_stdout(player_event)
                self._server._on_player_event(ctx)

            if player_event.event == Event.PLAYER_SAVED_THE_GAME:

                server_event = copy.copy(player_event)
                server_event.event = Event.GAME_SAVED

                ctx = self.process_parsed_stdout(server_event)

            for plugin in self._server.plugin_manager.plugins:
                
                if player_event.event not in plugin.events.keys():
                    continue
                
                for callback in plugin.events[player_event.event]:
                    
                    try:
                        if ctx is None:
                            ctx = self.process_parsed_stdout(player_event)

                        callback(ctx)
                    except Exception as e:
                        
                        if ctx is None:

                            plugin.logger.error(f"Context parsing error: {e}, for event: {player_event.event}")
                            return

                        ctx.error(e)

                        if ctx.player is None or ctx.player.name == PLAYER_NOT_SUPPORTED:
                            traceback.print_exc()
                        

    def dispatch_log_events(self, line: str) -> None:
        """
        Called at every line to dispatch the log events
        """

        for plugin in self._server.plugin_manager.plugins:

            if Event.ON_LOG not in plugin.events.keys():
                continue

            for callback in plugin.events[Event.ON_LOG]:
                try:
                    callback(line)
                except:
                    ...


    def fetch_other_events(self) -> None:
        """
        Fetches and dispatch events that aren't enabled by default
        """
        
        for listener in self._listeners:
            self._process_listener(listener)

        # for plugin in self._server.plugin_manager.plugins:
        #     ...


    def _process_listener(
        self,
        listener: Union[Event, EventListener]
    ) -> None:
        """
        Run every listener or event separately
        """
        
        if issubclass(listener.__class__, EventListener):
            
            if listener.enabled is True:
                try:
                    listener.tick()
                except:
                    pass

            if hasattr(listener, "_detach_flag"):
                if getattr(listener, "_detach_flag") is True:
                    self._listeners.remove(listener)

        return None


    def add_listener(
        self,
        listener: EventListener,
        *functions: Callable
    ) -> None:
        """
        Adds the given listener to the slots
        """

        self._listeners.append(listener)

        for f in functions:
            listener.add_fallback(f)
        
        return None