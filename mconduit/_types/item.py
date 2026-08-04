from mconduit.json import Serializable, Field


class Item(Serializable):
    """
    Represent an inventory item
    """


    name: Field[str, "id"] # type: ignore
    count: Field[int, None, 1] # type: ignore
    components: Field[dict | None, None, None] # type: ignore


    def __init__(
        self,
        name: str,
        count: int = 1,
        components: dict | None = None
    ) -> None:
    
        super().__init__()
        name = name.strip()

        if not name.startswith("minecraft:"):
            name = "minecraft:" + name

        self.name = name # type: ignore
        self.count = count # type: ignore
        self.components = components # type: ignore

    
    def __str__(self) -> str:
        return str(self.to_dict())
    

    def __repr__(self) -> str:

        components = ""
        
        if self.components is not None:
            components = f", components: {components}"

        return f"Item(name: '{self.name}', count: {self.count}{components})"