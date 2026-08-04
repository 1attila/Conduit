from __future__ import annotations
from typing import Union, Dict, List, Any, TYPE_CHECKING
import nbtlib # type: ignore[import-untyped]
import json
import gzip
import io

from mconduit.world.world_snapshot import WorldSnapshot
from mconduit.scoreboard.scoreboard import Scoreboard, Blank, Fixed, Styled
from mconduit.scoreboard.objective import Objective, RenderType
from mconduit.scoreboard.display_slot import DisplaySlot
from mconduit.scoreboard.team import Team
from mconduit.text.text import Text
from mconduit._types.player import Player

if TYPE_CHECKING:
    from mconduit.server_api import ServerAPI


def format_text(text_data: str) -> Text:

    if ":" in text_data and '"':
        
        try:
            text_dict = json.loads(text_data)
            
            return Text.from_dict(text_dict)
    
        except json.JSONDecodeError:
            pass

    return Text(text_data[1:-1])
    


class ScoreboardReader:
    """
    Class responsable to fetch and cache scoreboard and teams values
    """

    _data_version: int
    _scoreboards: Dict[str, Scoreboard]
    _objectives: Dict[str, Objective]
    _teams: Dict[str, Team]
    _display_slots: Dict[DisplaySlot, str]
    _server: ServerAPI
    _world_snapshot: WorldSnapshot


    def __init__(
        self,
        server: ServerAPI,
        world_snapshot: WorldSnapshot
    ) -> None:
        
        self._data_version = -1
        self._scoreboards = {}
        self._objectives = {}
        self._teams = {}
        self._display_slots = {}

        self._server = server
        self._world_snapshot = world_snapshot

    
    def _fetch(self) -> Dict[str, Union[List[Dict[str, Any]], Dict[str, str]]]:

        self._data_version = self._world_snapshot.data_version

        with open(self._world_snapshot.world_path / "data" / "scoreboard.dat", "rb") as f:

            data = f.read()
            data = gzip.decompress(data)
            data = io.BytesIO(data) # type: ignore

            nbt = nbtlib.File.parse(data)

            return nbt.unpack()["data"]

    
    def _fetch_objectives(self) -> None:

        data = self._fetch()

        for objective in data.get("Objectives", []):

            assert isinstance(objective, dict)
            
            if objective.get("RenderType", "integer") == "integer":
                render_type = RenderType.INTEGER
            else:
                render_type = RenderType.HEARTS

            objective_name = objective["Name"]

            self._objectives[objective_name] = Objective(
                objective["CriteriaName"],
                format_text(objective["DisplayName"]), # type: ignore
                objective_name,
                render_type,
                objective.get("display_auto_update", False),
                server=self._server
            )

    
    def _fetch_scoreboards(self) -> None:

        data = self._fetch()
        temp_scoreboards: Dict[str, Dict[str, Any]] = {} # objective-name -> data

        for score in data.get("PlayerScores", []):
            
            objective = score["Objective"] # type: ignore
            
            if objective not in temp_scoreboards:

                format = score.get("format", None) # type: ignore

                if format is not None:

                    match format["type"]: # type: ignore

                        case "blank":
                            format = Blank()

                        case "fixed":
                            format = Fixed(format_text(format["value"]))

                        case "styled":
                            format = Styled(Text.from_dict(format))

                display = score.get("display", None) # type: ignore

                if display is not None:
                    display = format_text(display)

                temp_scoreboards[objective] = {
                    "format": format,
                    "display": display,
                    "scores": []
                }

            temp_scoreboards[objective]["scores"].append(
                {
                    "score": score["Score"], # type: ignore
                    "player": score["Name"], # type: ignore
                    "locked": score.get("Locked", False) # type: ignore
                }
            )

        for objective_name, scoreboard in temp_scoreboards.items():
            
            self._scoreboards[objective_name] = Scoreboard(
                objective_name,
                scoreboard["display"],
                scoreboard["format"],
                scoreboard["scores"],
                server=self._server
            )


    def _fetch_teams(self) -> None:

        data = self._fetch()

        for team in data.get("Teams", []):
            
            players = [Player(p_name, self._server) for p_name in team["Players"]] # type: ignore
            
            team_name: str = team["Name"] # type: ignore
            
            self._teams[team_name] = Team(
                team["AllowFriendlyFire"], # type: ignore
                team["SeeFriendlyInvisibles"], # type: ignore
                team["NameTagVisibility"], # type: ignore
                team["DeathMessageVisibility"], # type: ignore
                team["CollisionRule"], # type: ignore
                format_text(team["DisplayName"]), # type: ignore
                team_name, # type: ignore
                format_text(team["MemberNamePrefix"]), # type: ignore
                format_text(team["MemberNameSuffix"]), # type: ignore
                team.get("TeamColor", None), # type: ignore
                players,
                server=self._server
            )

    
    def _fetch_display_slots(self) -> None:

        data = self._fetch()

        for slot, objective in data.get("DisplaySlots", {}).items(): # type: ignore
            self._display_slots[slot] = objective # type: ignore


    @property
    def data_version(self) -> int:
        """
        Data version of scoreboard.dat nbt structure
        """

        return self._data_version


    @property
    def scoreboards(self) -> Dict[str, Scoreboard]:
        """
        Server scoreboards
        """

        if len(self._scoreboards) == 0:
            self._fetch_scoreboards()
        
        return dict(self._scoreboards)


    @property
    def objectives(self) -> Dict[str, Objective]:
        """
        Scoreboard objectives
        """

        if len(self._objectives) == 0:
            self._fetch_objectives()
        
        return dict(self._objectives) 


    @property
    def teams(self) -> Dict[str, Team]:
        """
        Server teams
        """

        if len(self._teams) == 0:
            self._fetch_teams()

        return dict(self._teams)
    

    @property
    def display_slots(self) -> Dict[DisplaySlot, str]:
        """
        Indicates what scoreboard is displayed for each slot
        """

        if len(self._display_slots) == 0:
            self._fetch_display_slots()

        return dict(self._display_slots)


    def clear_cache(self) -> None:
        """
        Clears all the caches
        """

        self._data_version = -1
        self._scoreboards = {}
        self._objectives = {}
        self._teams = {}
        self._display_slots = {}