from typing import Optional, Dict, SupportsIndex, TypeVar, Type, Any, TYPE_CHECKING
from pathlib import Path
import threading
import copy
import json
import os


from mconduit import constants

if TYPE_CHECKING:
    from mconduit.plugins.plugin import Plugin


P = TypeVar("P", bound="Persistent")


class PersistentMixin:

    
    def __init__(self, owner: "Persistent", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._owner = owner


    def _wrap_value(self, value: Any) -> Any:
        return self._owner._wrap_value(value)


    def _save(self):
        self._owner._save()


class PersistentList(PersistentMixin, list):
    """
    Built-in mutable sequence.

    If no argument is given, the constructor creates a new empty list.

    The argument must be an iterable if specified.
    """


    def append(self, item, /):
        """
        Append object to the end of the list.
        """

        super().append(self._wrap_value(item))
        self._save()

    
    def insert(self, pos, item, /):
        """
        Insert object before index.
        """

        super().insert(pos, self._wrap_value(item))
        self._save()


    def extend(self, iterable, /):
        """
        Extend list by appending elements from the iterable.
        """

        super().extend(self._wrap_value(iterable))
        self._save()


    def __setitem__(self, index, value, /):
        """
        Set self[key] to value.
        """

        super().__setitem__(index, self._wrap_value(value))
        self._save()


    def __delitem__(self, index, /):
        """
        Delete self[key].
        """

        super().__delitem__(index)
        self._save()


    def pop(self, index: SupportsIndex = -1, /) -> Any:
        """
        Remove and return item at index (default last).

        Raises IndexError if list is empty or index is out of range.
        """
        
        ret = super().pop(index)
        self._save()

        return ret


    def remove(self, value: Any, /) -> Any:
        """
        Remove first occurrence of value.

        Raises ValueError if the value is not present.
        """
        
        ret = super().remove(value)
        self._save()

        return ret


class PersistentDict(PersistentMixin, dict):
    """
    dict() -> new empty dictionary

    dict(mapping) -> new dictionary initialized from a mapping object's

    (key, value) pairs

    dict(iterable) -> new dictionary initialized as if via:

    d = {}

    for k, v in iterable:
    
        d[k] = v

    dict(**kwargs) -> new dictionary initialized with the name=value pairs

    in the keyword argument list. For example: dict(one=1, two=2)
    """


    def __setitem__(self, key, value, /):
        """
        Set self[key] to value.
        """

        super().__setitem__(key, self._wrap_value(value))
        self._save()


    def __delitem__(self, key, /):
        """
        Delete self[key].
        """

        super().__delitem__(key)
        self._save()


    def update(self, *args, **kwargs):

        super().update(*args, **kwargs)
        self._save()


    def pop(self, key: Any, default: Optional[Any]=None, /):
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.

        If the key is not found, return the default if given; otherwise,

        raise a KeyError.
        """

        if default is not None:

            ret = super().pop(key, default)
            self._save()
        
        else:
            ret = super().pop(key)
            self._save()

        return ret
    

    def setdefault(self, key: str, default: Optional[Any]=None, /) -> Optional[Any]:
        
        ret = super().setdefault(key, self._wrap_value(default))
        self._save()

        return ret


class PersistentSet(PersistentMixin, set):
    """
    Build an unordered collection of unique elements.
    """


    def add(self, item, /):
        """
        Add an element to a set.

        This has no effect if the element is already present.
        """

        super().add(self._wrap_value(item))
        self._save()


    def remove(self, item, /):
        """
        Remove an element from a set; it must be a member.

        If the element is not a member, raise a KeyError.
        """

        super().remove(item)
        self._save()


    def discard(self, item, /):
        """
        Remove an element from a set if it is a member.

        Unlike set.remove(), the discard() method does not raise an exception when an element is missing from the set.
        """

        super().discard(item)
        self._save()


class NoValue:
    ...


class MissingDefaultPersistentValue(Exception):
    ...


class Persistent:
    """
    Persistent state to save values  
    """

    _path: Path
    _lock: threading.RLock

    
    @classmethod
    def load(cls: Type[P], plugin: "Plugin") -> P:
        """
        Loads the values present in `persistent.json` inside the plugin folder.

        If there is no persistent file it generates one with the proper fields
        """

        self = cls()
        self._lock = threading.RLock()
        self._path = Path(constants.PLUGINS_DIR) / plugin.name / plugin.server.name / constants.PERSISTENT_FILENAME

        if not self._path.exists(): 

            self._load_default_annotations()
            data = self._get_class_attributes()

            if len(data) > 0:
                
                self._path.parent.mkdir(parents=True, exist_ok=True)

                with open(self._path, "w") as f:
                    json.dump(data, f, indent=4)
            
            return self

        try:
            with self._lock:
                
                with open(self._path, "r") as f:
                    loaded = json.load(f)
                
        except json.JSONDecodeError:
            loaded = {}

        self._load_default_annotations()
        
        for k, v in loaded.items():

            v = self._wrap_value(v)
            self.__dict__[k] = v
        
        self._save()

        return self
    

    def _load_default_annotations(self) -> None:
        """
        Loads into self.__dict__ it's annotated values names with their real value.

        Raises if this instance contains non-initialized value
        """

        for item, _annotation in getattr(type(self), "__annotations__", {}).items():
                
            if item.startswith("_"):
                continue

            value = getattr(type(self), item, NoValue)

            if value is NoValue:
                raise MissingDefaultPersistentValue()

            value = self._wrap_value(value)

            if isinstance(value, (PersistentList, PersistentDict, PersistentSet)):

                self.__dict__[item] = copy.copy(value)
            else:            
                self.__dict__[item] = copy.deepcopy(value)
    

    def _get_class_attributes(self) -> Dict[str, Any]:
        """
        Returns everything inside self.__dict__ that doesn't start with an underscore
        """

        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


    def _save(self):

        data = self._get_class_attributes()

        if not data:
            return

        if not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)

        temp_path = self._path.with_suffix(".tmp")

        with self._lock:

            with open(temp_path, "w") as f:

                json.dump(data, f, indent=4)
                f.flush()
                os.fsync(f.fileno())

            os.replace(temp_path, self._path)


    def has_item(self, item: str) -> bool:
        """
        Returns True if a variable with the given name it's stored here
        """

        return item in self._get_class_attributes()

    
    def get_or(self, item: str, value: Any) -> Any:
        """
        Returns the item with the given name.

        If it doesnt exists it sets the given value and returns that
        """

        if self.has_item(item):
            return self.__dict__[item]

        self.__dict__[item] = value
        self._save()

        return value


    def _wrap_value(self, value: Any) -> Any:

        if isinstance(value, list):
            return PersistentList(self, value)

        elif isinstance(value, dict):
            return PersistentDict(self, value)

        elif isinstance(value, set):
            return PersistentSet(self, value)

        return value


    def __setattr__(self, name, value):

        if name.startswith("_"):
            super().__setattr__(name, value)

        else:
            
            value = self._wrap_value(value)
            
            self.__dict__[name] = value
            self._save()