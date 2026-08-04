from typing import Callable, Dict, Any


class CachedStructure:
    """

    """


    _cache: Dict[str, Any]


    def __init__(self) -> None:
        
        self._cache = {}


    def _get_or_fetch(
        self,
        key: str,
        fn: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        
        """

import nbtlib
import gzip
import io


for item in ["scoreboard.dat", "raids.dat", "chunks.dat", "random_sequences.dat"]:

    with open(f"C:\\Users\\Hp\\Desktop\\handler\\MCDR\\server\\world\\data\\{item}", "rb") as f:

        data = (f.read())
        data = gzip.decompress(data)
        data = io.BytesIO(data)

        nbt = nbtlib.File.parse(data)
        print(nbt.unpack())

for item in ["level.dat", "level.dat_old", "playerdata\\378f2d9a-f709-32e1-923f-c99530ee0fce.dat"]:

    with open(f"C:\\Users\\Hp\\Desktop\\handler\\MCDR\\server\\world\\{item}", "rb") as f:

        data = (f.read())
        data = gzip.decompress(data)
        data = io.BytesIO(data)

        nbt = nbtlib.File.parse(data)
        print(nbt.unpack())

while True:...
