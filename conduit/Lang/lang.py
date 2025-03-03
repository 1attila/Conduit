from typing import Optional, NoReturn, Dict
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
    __lang_dict: Dict


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
    

    def __getitem__(self, id: str) -> Optional[str]:
        
        try:
            return self.__lang_dict[id]
        except KeyError:
            return None


    @property
    def lang(self) -> str:
        return self.__lang
    
    
    def set_lang(self, value: str) -> bool:
        
        if self._load_lang(value):

            self.__lang = value
            return True
        
        return False