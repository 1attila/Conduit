from typing import Union, Tuple, List, Dict, Callable, TYPE_CHECKING

from mconduit.text.text import Text
from mconduit.utils.scoreboards import get_latest_trigger_id, list_scoreboards
from mconduit.stdout_parser import ParsedResult
from mconduit.context import Context
from mconduit.event import Event

if TYPE_CHECKING:
    from mconduit.base_server import BaseServer


TEXT_SCOREBOARD_PREFIX = "mconduit-text-"


class TextHandler:
    """
    Looks for events
    """


    _server: "BaseServer"
    _text_binds: Dict[int, List[Callable]]
    _latest_trigger_id: int # Cached to avoid fetching it every time


    def __init__(self, server: "BaseServer") -> None:

        self._server = server
        self._text_binds = {}
        self._latest_trigger_id = get_latest_trigger_id(self._server, TEXT_SCOREBOARD_PREFIX) # type: ignore


    def bind_text(
        self,
        text: Text,
        button_id: int = 0,
        scoreboard_id: int = -1,
        text_chunk: bool = False
    ) -> Union[Text, Tuple[Text, int]]:
        """
        Binds all the click events present in this text, and returns the text ready to be print
        """

        with self._server.all_at_once():

            if text.click_action is not None and text.click_action[0] == "run_function":
            
                if scoreboard_id == -1:
                
                    scoreboard_id = self._latest_trigger_id
                    self._latest_trigger_id += 1
            
                self._text_binds.setdefault(scoreboard_id, []).append(text.click_action[1])

                s_name = f"{TEXT_SCOREBOARD_PREFIX}{scoreboard_id}-{button_id}"

                self._server.execute([
                    f'/scoreboard objectives add {s_name} trigger "{s_name}"',
                    f"/scoreboard players enable @a {s_name}"
                ])

                text = text.click(run_command=f"/trigger {s_name}")
                button_id += 1

            for i, item in enumerate(text.text_bits):

                if item.click_action is not None and item.click_action[0] == "run_function":

                    text.text_bits[i], scoreboard_id = self.bind_text(item, button_id, scoreboard_id, True) # type: ignore
                    button_id += 1

            if text_chunk is True:
                return text, scoreboard_id

        return text

    
    def on_player_trigger(self, pr: ParsedResult) -> None:
        
        trigger = pr.infos["message"][len(TEXT_SCOREBOARD_PREFIX):] # type: ignore
        id, button_id = trigger.split("-")

        id = int(id)
        button_id = int(button_id)

        if id in self._text_binds:
            
            try:
                fn = self._text_binds[id][button_id]
                context = Context(pr.player, pr.time, pr.server, Event.TEXT_CLICK, id=button_id)
                fn(context)

            except Exception as e:
                Context(pr.player, pr.time, pr.server, Event.TEXT_CLICK).error(e)


    def reset(self) -> None:
        
        text_scoreboards = list_scoreboards(self._server, prefix=TEXT_SCOREBOARD_PREFIX) # type: ignore
        self._text_binds = {}

        with self._server.all_at_once():
            
            for scoreboard in text_scoreboards:
                self._server.execute(f"/scoreboard objectives remove {scoreboard}")