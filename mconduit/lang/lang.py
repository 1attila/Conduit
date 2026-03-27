from typing import List, Dict
from pathlib import Path
import yaml
import os


class Lang:
    """
    Language class to get the rigth translation

    Usage:
    server.lang["translation-id"]
    """

    __lang: str
    __path: Path
    __lang_dict: Dict[str, str]


    def __init__(
        self,
        path: Path,
        default_lang: str
    ) -> None:

        self.__path = Path(path)
        
        if self._load_lang(default_lang):
            self.__lang = default_lang
        else:
            raise ValueError

    
    def _load_lang(self, lang: str) -> bool:

        path = self.__path / f"{lang}.yml"

        if not path.exists():
            return False
        
        with open(path) as f:

            self.__lang_dict = yaml.safe_load(f)
            self.__lang = lang
            
            return True

        return False
    

    def __getitem__(self, *args: str) -> str:

        try:
            args = list(args)
            
            string = self.__lang_dict[args.pop(0)]
            
            for id, item in enumerate(args):
                string = string.replace("{" + str(id) + "}", item)

            return string

        except KeyError:
            return "<item not found>"


    @property
    def lang(self) -> str:
        return self.__lang

    
    @property
    def avaiable_langs(self) -> List[str]:
        """
        All the languages that can be used
        """

        langs = [item.replace(".yml", "") for item in os.listdir(self.__path) if item.endswith(".yml")]
        
        if "en_us" in langs:
            langs.remove("en_us")
            langs.insert(0, "en_us")
        
        return langs
    
    
    def set_lang(self, value: str) -> bool:
        """
        Sets the new lang, if possible.

        Returns True if it could be changed, False otherwise
        """

        return self._load_lang(value)