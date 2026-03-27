from typing import Optional, List, Dict, TYPE_CHECKING
from pathlib import Path
import threading
import shutil
import json
import os

from .resource_saver import sha1 # NOTE: this does not support external machines!
from .resource_server import ResourcePackHTTPServer
from ..sound import Sound, InvalidSoundExtension, convert_to_ogg

if TYPE_CHECKING:
    from ..server import Server


DEFAULT_PACK_FORMAT = 34
PACK_MCMETA_FILENAME = "pack.mcmeta"
ASSETS_DIR = "assets"
SUPPORTED_SOUND_EXT = {".ogg", ".mp3", ".wav", ".flac", ".m4a", ".aac"}


class SoundAlreadyExists(Exception):
    ...


class ResourcePack:
    """
    Conduit resource pack.

    This can be used to play custom sounds and a lot more! 
    """

    NAME = "mconduit-resource-pack"
    NAMESPACE = "mconduit"

    BASE_DEV_PATH =  Path(".mconduit-resource-pack-dev")
    BASE_FINAL_PATH = Path("mconduit-resource-pack-release")
    
    __server: "Server"
    __pack_format: int
    __lock: threading.Lock
    __http_server: Optional[ResourcePackHTTPServer]


    def __init__(
        self,
        server: "Server",
        pack_format: int=DEFAULT_PACK_FORMAT
    ) -> None:
        
        self.__server = server
        self.__pack_format = pack_format
        self.__lock = threading.Lock()
        self.__http_server = None

        if self.final_path.exists():
            self._load_http_server()
        
        self._setup()

    
    def _setup(self) -> None:
        """
        Creates the dev path (where the resource pack is built and stored uncompressed)
        """

        self.dev_dir.mkdir(parents=True, exist_ok=True)
        self.final_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            mc_meta = json.dumps(self.pack_mcmeta, indent=4)

        except Exception as e:

            print(f"Unable to create resource pack for {self.__server.name}, error:", e)
            return

        (self.dev_dir / PACK_MCMETA_FILENAME).write_text(mc_meta)

    
    def _load_http_server(self) -> None:

        if self.__server.config.resource_pack_config is not None:
            if self.__server.config.resource_pack_config.enabled is False:
                return

        if self.__http_server is None:
            self.__http_server = ResourcePackHTTPServer(
                self.final_path.parent
            ) # TODO: Add some configs to set different host and port

    
    @property
    def pack_format(self) -> int:
        """
        Pack format
        """

        return self.__pack_format
    

    @property
    def pack_mcmeta(self) -> Dict:
        """
        A dict containing the fields in the pack.mcmeta file
        """

        return {
            "pack": {
                "pack_format": self.__pack_format,
                "description": self.NAME
            }
        }

    
    @property
    def dev_dir(self) -> Path:
        """
        The directory where this resource pack is assembled
        """

        return self.BASE_DEV_PATH / self.__server.name

    
    @property
    def final_path(self) -> Path:
        """
        Server resource pack path, where this resource pack its stored zipped
        """
        
        return (self.BASE_FINAL_PATH / self.__server.name / self.NAME).with_suffix(".zip")

    
    @property
    def sounds_dir(self) -> Path:
        """
        Returns the path of the directory where all the sounds are located.

        It may not exist
        """

        return (self.dev_dir / ASSETS_DIR / self.NAMESPACE / "sounds")


    @property
    def sounds_json_path(self) -> Path:
        """
        Returns the path of the sounds.json file.

        It may not exist
        """

        return (self.dev_dir / ASSETS_DIR / self.NAMESPACE / "sounds.json")


    def ensure_sounds_dir(self) -> None:
        """
        Creates the sounds dir and sounds.json files
        """

        with self.__lock:

            if not self.sounds_dir.exists():
                self.sounds_dir.mkdir(parents=True, exist_ok=True)

            if not self.sounds_json_path.exists():
                self.sounds_json_path.write_text("{}")


    @property
    def sounds(self) -> Dict[str, List[Sound]]:
        """
        A dict containing the mapping command-name --> sounds
        """

        if not self.sounds_json_path.exists():
            return {}

        with self.__lock:
            with open(self.sounds_json_path) as f:
                sounds_json: Dict = json.load(f)
        
        sounds = {}

        for command_name, command_sounds in sounds_json.items():
            sounds[command_name] = [
                Sound(
                    Path(self.remove_namespace(sound["name"])),
                    sound["stream"]
                )
                for sound in command_sounds["sounds"]
            ]

        return sounds

    
    def _process_sound(self, sound: Sound) -> Sound:

        sound_path = Path(sound.file_path)
        
        if not sound_path.is_file():
            raise ValueError("The given sound path is not a file")

        if not sound_path.suffix.lower() in SUPPORTED_SOUND_EXT:
            raise InvalidSoundExtension
        
        sound.file_path = self.sounds_dir / self.clear_resource_name(sound_path.with_suffix(".ogg").name)
        convert_to_ogg(sound_path, sound.file_path)

        return sound

    
    def add_sounds(self, sound_name: str, *sounds: Sound) -> None:
        """
        Adds the given sound to this resource pack
        """

        if sound_name in self.sounds.keys():
            raise SoundAlreadyExists

        sounds_mapping = self.sounds
        self.ensure_sounds_dir()
        
        new_sounds = [self._process_sound(sound) for sound in sounds]

        sounds_mapping[sound_name] = new_sounds
        sounds_mapping = { # type: ignore
            k: {
                "sounds": [
                    {
                        "name": f"{self.NAMESPACE}:{item.file_path.with_suffix('').name}",
                        "stream": item.stream
                    } for item in v
                ]
            } for k, v in sounds_mapping.items()
        }

        with self.__lock:
            with open(self.sounds_json_path, "w") as f:

                sounds_json = json.dumps(sounds_mapping, indent=4)
                f.write(sounds_json)

    
    def clear_resource_name(self, name: str) -> str:

        TO_REPLACE = [" ", "-", "_", "(", ")", "[", "]"]
        
        for to_replace in TO_REPLACE:
            name = name.replace(to_replace, "")

        return name.lower()

    
    def remove_namespace(self, name: str) -> str:
        return name.removeprefix(f"{self.NAMESPACE}:")


    def _stop_and_update(self) -> None:
        """
        Zip the resource pack and modifies server.properties resource pack link.

        Note: this should be called ONLY by Server when it shuts down
        """
        
        if self.__http_server is not None:
            self.__http_server.stop()

        if len(os.listdir(self.dev_dir)) < 2:
            return
        
        shutil.make_archive(self.final_path.with_suffix(""), "zip", root_dir=self.dev_dir) # type: ignore

        self._load_http_server()
        
        self.__server.resource_pack_sha1 = sha1(self.final_path)

        if self.__http_server is not None:
            self.__server.resource_pack_url = self.__http_server.url_for(self.final_path.name)
    
    
    def _serve(self) -> None:
        """
        Serves the resource pack so players can download it.

        Note: this should be called ONLY by Server when it starts
        """

        if not self.final_path.exists() or len(os.listdir(self.final_path.parent)) == 0:
            return
        
        self._load_http_server()

        if self.__http_server is not None:
            self.__http_server.start()