from typing import NoReturn, List, Dict
from pathlib import Path

import yaml
    

class Lang:
    """
    Language class to get the rigth translation

    Usage:
    server.lang["translation-id"]
    """

    __lang: str
    __path: Path
    __lang_dict: Dict[str, str]


    def __init__(self, path: Path, default_lang: str) -> NoReturn:

        self.__path = path
        
        if self._load_lang(default_lang):
            self.__lang = default_lang
        else:
            raise ValueError

    
    def _load_lang(self, lang: str) -> bool:
        
        with open(f"{self.__path}\\{lang}.yml") as f:

            self.__lang_dict = yaml.safe_load(f)
            self.__lang = lang
            
            return True

        return False
    

    def __getitem__(self, args: List[str]) -> str:

        if isinstance(args, tuple):
            args = list(args)
        else:
            args = [args]

        try:
            string = self.__lang_dict[args.pop(0)]
            
            for id, item in enumerate(args):
                string = string.replace("{" + str(id) + "}", item)

            return string

        except KeyError:
            return "<item not found>"


    @property
    def lang(self) -> str:
        return self.__lang
    
    
    def set_lang(self, value: str) -> bool:
        
        if self._load_lang(value):

            self.__lang = value
            return True
        
        return False