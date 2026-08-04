from typing import Optional, Dict, List, Any


class Field:
    """
    Json object field.

    This could be used as a type annotation to set default values and override the name
    """


    def __init__(
        self,
        type: object,
        override_name: str | None = None,
        defaults: List[Any] | None = None
    ) -> None:
        
        self.type = type
        self.defaults = defaults or []
        self.override_name = override_name
    

    @classmethod
    def __class_getitem__(cls, items) -> "Field":
        
        if not isinstance(items, tuple):
            items = (items, )

        items = list(items)
        
        type = items.pop(0)

        if len(items) > 0:
            override_name = items.pop(0)
        else:
            override_name = None

        if len(items) > 0:
            defaults = list(items)
        else:
            defaults = None

        return Field(
            type,
            override_name,
            defaults
        )
    

class Serializable:
    """
    Inherit this class to create custom nbt or json like serializable structures.

    Example:
    ```
    class Dialog(Serializable):
        type: Field[str]
        title: Field[str]
        external_title: Field[str]
        body: Field[list[dict]]
        inputs: Field[list[dict]]
        can_close_with_escape: Field[bool, None, True]
        pause: Field[bool, None, True]
        after_action: Field[str]

    my_dialog = Dialog()
    my_dialog.type = "minecraft:notice"
    my_dialog.title = "My custom dialog"
    my_dialog.pause = True # Note: it's already the default value
    dialog_dict = my_dialog.to_dict()
    {
        "type": "minecraft:notice",
        "title": "My custom dialog"
    } # Note: No `pause` field because it's already as it's default value
    ```
    """


    def __init__(self) -> None:
        
        self._fields = {}

        for k, v in getattr(self, "__annotations__", {}).items():

            if type(v) is Field:
                self._fields[k] = v

    
    def add_field(
        self,
        name: str,
        field: Field
    ) -> None:
        self._fields[name] = field

    
    def get_field(self, field_name: str) -> Optional[Field]:
        return self._fields.get(field_name, None)
        

    def to_dict(self, **kwargs) -> Dict[str, Any]:
        """
        Returns a dict with all the class fields
        """
        
        out = {}

        for field_name, field in self._fields.items():
            
            class NoValue:...

            item = getattr(self, field_name, NoValue)
            key = field.override_name if field.override_name is not None else field_name
            
            if item != NoValue and item not in field.defaults:

                if isinstance(item, Serializable):
                    item = item.to_dict(**kwargs)
                 
                out[key] = item

        return out