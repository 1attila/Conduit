"""
Utility tool to update/sync all the translations entries
"""

from typing import List
from pathlib import Path
import yaml
import re
import os

from mconduit.constants import CONDUIT_PATH

DEFAULT_PATTERNS = [
    re.compile(r'(?<!\w)self\.lang\["([^"]+)"\]'),
    re.compile(r'(?<!\w)l\["([^"]+)"\]')
]


class LangSyncer:

    def __init__(
        self,
        langs_directory: Path = CONDUIT_PATH / "resources",
        code_directory: Path = CONDUIT_PATH,
        parser_regexes: List[re.Pattern] = DEFAULT_PATTERNS,
        default_lang: str = "en_us"
    ) -> None:

        self.langs_directory = Path(langs_directory)
        self.code_directory = Path(code_directory)
        self.patterns = parser_regexes
        self.default_lang = default_lang


    def _fetch_translation_entries(self) -> List[str]:

        translations = []

        for root, _, files in os.walk(self.code_directory, topdown=True):
            
            for file in files:
                
                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(root, file)
                
                with open(file_path, "r", errors="ignore") as f:

                    for line in f:

                        for pattern in self.patterns:
                            
                            matched = pattern.search(line)

                            if matched:
                                translations.append(matched.group(1))

        return translations

    
    def _fix_translation_file(
        self,
        lang_filename: str,
        entries: List[str],
        update_file: bool = True
    ) -> None:
        
        try:
            with open(lang_filename, encoding="utf-8") as f:
                lang = yaml.safe_load(f) or {}

        except FileNotFoundError:
            lang = {}

        updated = False

        for k in entries:
            
            if k not in lang:

                print(f"Missing translation @ {Path(lang_filename).name}, key:", k)
                
                if Path(lang_filename).name == f"{self.default_lang}.yml":

                    lang[k] = k
                    updated = True
        
        if update_file is True and updated is True:

            with open(lang_filename, "w", encoding="utf-8") as f:
                yaml.safe_dump(lang, f, allow_unicode=True)


    def run(
        self,
        update_file: bool = True
    ) -> None:
        
        entries = self._fetch_translation_entries()
        
        for lang in os.listdir(self.langs_directory):

            if lang.endswith(".yml"):
                self._fix_translation_file(os.path.join(self.langs_directory, lang), entries, update_file)