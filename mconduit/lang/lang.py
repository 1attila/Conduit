from typing import List, Tuple, Dict
from pathlib import Path
import yaml
import os
import re


REGEX_PATTERN = r"\{.*?\}"


class Lang:
    """
    Language class to get the rigth translation

    Usage:
    server.lang["translation-id"]
    """

    _lang: str
    _path: Path
    _lang_dict: Dict[str, str]
    _entries_regexes: List[Tuple[re.Pattern, str, List[str]]]


    def __init__(
        self,
        path: Path,
        default_lang: str
    ) -> None:

        self._path = Path(path)
        
        if self._load_lang(default_lang):
            self._lang = default_lang
        else:
            raise ValueError(f"Language file {default_lang}.yml not found or corrupted!")

    
    def _load_lang(self, lang: str) -> bool:

        path = self._path / f"{lang}.yml"

        if not path.exists():
            return False
        
        with open(path, "r", encoding="utf-8") as f:

            self._lang_dict = yaml.safe_load(f) or {}

            self._entries_regexes = []

            sorted_keys = sorted(self._lang_dict.keys(), key=len, reverse=True)

            for key in sorted_keys:

                value = self._lang_dict[key]

                if re.search(REGEX_PATTERN, key):

                    placeholders = re.findall(REGEX_PATTERN, key)
                    parts = re.split(REGEX_PATTERN, key)
                    escaped_parts = [re.escape(part) for part in parts]

                    regex_pattner = "^" + "(.*)".join(escaped_parts) + "$"

                    self._entries_regexes.append(
                        (re.compile(regex_pattner), value, placeholders)
                    )

            self._lang = lang
            
            return True

        return False
    

    def __getitem__(self, key: str) -> str:


        if key in self._lang_dict:
            return self._lang_dict[key]
        
        for pattern, value, placeholders in self._entries_regexes:

            match = pattern.fullmatch(key)

            if match is not None:

                variables = match.groups()
                kwargs: Dict[str, str] = {}

                for i, name in enumerate(placeholders):
                    
                    clean_name = name.strip("{}")
                    kwargs[clean_name] = variables[i]

                try:
                    return value.format(**kwargs)
                
                except (KeyError) as e:
                    pass

        return key


    @property
    def lang(self) -> str:
        return self._lang

    
    @property
    def avaiable_langs(self) -> List[str]:
        """
        All the languages that can be used
        """

        langs = [item.replace(".yml", "") for item in os.listdir(self._path) if item.endswith(".yml")]
        
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