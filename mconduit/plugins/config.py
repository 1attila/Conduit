from typing import TypeVar, Type, TYPE_CHECKING
from pathlib import Path
import json

from .. import constants 

if TYPE_CHECKING:
    from .plugin import Plugin


C = TypeVar("C", bound="Config")


class NoValue:
    ...


class Config:
    """
    Base class that represent plugin's config.

    Config are always named `config.json` and are inside the plugin folder

    Usage:
    ```
    class MyConfig(plugins.Config):
        my_value: str=None

    class MyPlugin(plugins.Plugin[MyConfig]):
        ...
    ```
    """

    
    __path: Path
    
    
    @classmethod
    def load(cls: Type[C], plugin: "Plugin") -> C:
        """
        Loads the values present in `config.json` inside the plugin folder.

        If there is no config file it generates one with the proper fields
        """

        instance = cls()
        instance.__plugin = plugin # type: ignore
        cls.__path = Path(constants.PLUGINS_DIR) / plugin.name / constants.CONFIG_FILENAME

        if not cls.__path.exists():
            
            configs = {}

            for item in getattr(cls, "__annotations__", {}):
                
                if item.startswith("_"):
                    continue
                
                value = getattr(cls, item, NoValue)

                if value is NoValue:
                    configs[item] = ""
                else:
                    configs[item] = value

            with open(cls.__path, "w") as f:
                json.dump(configs, f, indent=4)

        with open(cls.__path, "r") as f:
            
            configs = json.load(f)

            for k, v in configs.items():
                setattr(cls, k, v)

            for item in getattr(cls, "__annotations__", {}): # In case the plugin has updated it's configs
                
                if item.startswith("_"):
                    continue
                
                value = getattr(cls, item, NoValue)

                if value is NoValue:
                    configs[item] = ""
                else:
                    configs[item] = value

        with open(cls.__path, "w") as f: # In case the plugin has updated it's configs
            json.dump(configs, f, indent=4)

        return instance


    def save(self) -> None:
        """
        Saves the current configs into the json file
        """

        configs = {}

        for item, value in self.__dict__.items():
                
                if item.startswith("_"):
                    continue

                if value is not None:
                    configs[item] = value
                else:
                    configs[item] = ""

        with open(self.__path, "w") as f:
            json.dump(configs, f, indent=4)