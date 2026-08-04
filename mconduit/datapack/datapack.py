from typing import Dict, TYPE_CHECKING
from pathlib import Path
import logging
import shutil
import json

if TYPE_CHECKING:
    from ..server import Server
    from ..plugins import Plugin


logger = logging.getLogger(__name__)

DEFAULT_PACK_FORMAT = 88
PACK_MCMETA_FILENAME = "pack.mcmeta"


class Datapack:
    """
    Conduit datapack.

    This can be used to execute commands faster or every tick 
    """

    NAME = "mconduit-datapack"
    NAMESPACE = "mconduit"

    BASE_DEV_PATH = Path(".mconduit-datapack-dev")
    BASE_FINAL_PATH = Path("mconduit-datapack-release")

    _pack_format: int
    _loads: Dict[str, str]
    _ticks: Dict[str, str]


    def __init__(
        self,
        server: "Server",
        pack_format: int = DEFAULT_PACK_FORMAT
    ) -> None:
        
        self._server = server
        self._pack_format = pack_format
        self._loads = []
        self._ticks = []


    @property
    def dev_dir(self) -> Path:
        return self.BASE_DEV_PATH / self._server.name

    
    @property
    def final_path(self) -> Path:
        return self.BASE_FINAL_PATH / self._server.name

    
    @property
    def pack_mcmeta(self) -> Dict:

        return {
            "pack": {
                "description": self.NAME,
                "pack_format": self._pack_format
            }
        }
    
    
    def gen_structure(self) -> None:

        self.dev_dir.mkdir(parents=True, exist_ok=True)
        self.final_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            mc_meta = json.dumps(self.pack_mcmeta, indent=4)
        
        except Exception as e:
            logger.error(f"Unable to create datapack pack for {self._server.name}, error: ", e)
            return

        (self.dev_dir / PACK_MCMETA_FILENAME).write_text(mc_meta)

        funcs_dir = self.dev_dir / "data" / self.NAMESPACE / "functions"
        tags_dir = self.dev_dir / "data" / "minecraft" / "tags" / "functions"

        funcs_dir.mkdir(parents=True, exist_ok=True)
        tags_dir.mkdir(parents=True, exist_ok=True)

        for plg_name, l_code in self._loads.items():
            (funcs_dir / "load" / (plg_name + ".mcfunction")).write_text(l_code)

        for plg_name, t_code, in self._ticks.items():
            (funcs_dir / "tick" / (plg_name + ".mcfunction")).write_text(t_code)

        (tags_dir / "load.json").write_text(json.dumps({"values": [self.NAMESPACE + ":load/" + p for p in self._loads.keys()]}))
        (tags_dir / "tick.json").write_text(json.dumps({"values": [self.NAMESPACE + ":tick/" + p for p in self._ticks.keys()]}))


    def reload(self) -> None:
        """
        Reloads this datapack into the server
        """

        self.gen_structure()

        if self.final_path.exists():
            shutil.rmtree(self.final_path)
        
        shutil.copytree(self.dev_dir, self.final_path)
        
        self._server.execute("reload")


    def add_load(
        self,
        plg: "Plugin",
        *code: str
    ) -> None:
        """
        Execute these commands every time the datapack loads/reloads
        """

        self._loads[plg.name] = "\n".join(code)
        
        self.reload()


    def add_tick(
        self,
        plg: "Plugin",
        *code: str
    ) -> None:
        """
        Execute these commands every gametick
        """

        self._ticks[plg.name] = "\n".join(code)
        
        self.reload()