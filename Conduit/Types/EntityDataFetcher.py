from typing import Optional, TYPE_CHECKING
import parse


if TYPE_CHECKING:
    from Conduit.Server import Server


class EntityDataFetcher:
    """
    Contains utility methods to fetch entity data
    """
    

    FORMATTER = r"{player:d} has the following entity data: {data:d}"
    __server: "Server" # Initialized from Entity
    __name: str # Initialized from Entity


    def __fetch(self, attribute: str) -> Optional[str]:
        
        response = self.__server.execute(f"/data get entity {self.__name} {attribute}")
        
        if response:

            parsed = parse.parse(self.FORMATTER, response)
            
            return  None if parsed["data"] is None else parsed["data"]