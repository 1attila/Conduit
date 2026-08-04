from __future__ import annotations
from typing import Optional, Tuple, Dict, Any, overload
from collections import OrderedDict
from pathlib import Path
from abc import ABC
import threading
import nbtlib # type: ignore[import-untyped]
import struct
import math
import zlib
import gzip
import io

from mconduit.world.world_snapshot import WorldSnapshot
from mconduit.utils.coords import chunk_coords
from mconduit._types.vec3d import Vec3d
from mconduit.enums import Dimension


MAX_CACHED_REGIONS = 8
MAX_CACHED_CHUNKS = 128


def get_region_filename(
    x: int,
    z: int
) -> str:
    return f"r.{x}.{z}.mca"


def chunk_to_region(
    chunk_x: int,
    chunk_z: int
) -> Tuple[int, int]:
    return chunk_x // 32, chunk_z // 32


class Block(nbtlib.Compound):
    """
    Represents a Minecraft block
    """


    def __init__(
        self,
        block_data: nbtlib.Compound
    ) -> None:
        super().__init__(block_data.unpack())


    @property
    def name(self) -> str:
        """
        Block name
        """

        return self["Name"].replace("minecraft:", "")


    def __contains__(self, item) -> bool:
        return super().__contains__(item)

    
    def __getitem__(self, item) -> Any:
        return super().__getitem__(item)

    
    def __setitem__(self, key, value) -> None:
        return super().__setitem___(key, value)


    def __delitem__(self, item) -> None:
        return super().__delitem__(item)
    

    def __str__(self) -> str:
        return self.name


    def __eq__(self, other: object) -> bool:

        if isinstance(other, Block): # TODO
            raise NotImplementedError

        return self.name == str(other)


class SubChunk:
    """
    Represents a Minecraft sub-chunk.

    It holds the block-states and palette data
    """

    palette: nbtlib.Base
    data: nbtlib.Base


    def __init__(
        self,
        data: nbtlib.Base
    ) -> None:

        self.palette = data["block_states"]["palette"]
        self.data = data["block_states"].get("data")


class Chunk:
    """
    Represents a Minecraft chunk.

    Can be used to fetch the blocks inside
    """

    _data: nbtlib.Base
    sections: Dict[int, SubChunk]


    def __init__(
        self,
        nbt: nbtlib.Base
    ) -> None:
        
        self._data = nbt
        self.sections = {}
        
        for section in self._data.get("sections", []):

            y = int(section["Y"])
            self.sections[y] = SubChunk(section)
    

    @property
    def x(self) -> int:
        """
        Chunk x coordinate
        """

        return self._data["xPos"]


    @property
    def z(self) -> int:
        """
        Chunk z coordinate
        """

        return self._data["zPos"]

    
    def get_block(
        self,
        x: int,
        y: int,
        z: int
    ) -> Block:
        """
        Returns the block at the given coords (they can also be relative to this chunk)
        """
        
        x = round(x)
        y = round(y)
        z = round(z)

        section_y = int(y // 16)
        section = self.sections[section_y]

        palette = section.palette
        data = section.data

        if data is None:
            return Block(palette[0])

        local_x = x % 16
        local_y = y % 16
        local_z = z % 16

        index = (local_y * 16 + local_z) * 16 + local_x

        bits_per_block = max(4, math.ceil(math.log2(len(palette))))
        blocks_per_long = 64 // bits_per_block

        long_index = index // blocks_per_long
        bit_index = (index % blocks_per_long) * bits_per_block

        if long_index >= len(data):
            return Block(palette[0])
                
        value = (data[long_index] >> bit_index) & ((1 << bits_per_block) - 1)

        return Block(palette[int(value)])
            
    
    def get_height(
        self,
        x: int,
        z: int,
        type: str = "WORLD_SURFACE", # TODO: This might be replaced with an Enum
        min_y: int = -64
    ) -> int:
        """
        Returns the highest Y on the given x and y coordinates (they can also be relative to this chunk)
        """
        
        data = self._data.get("Heightmaps")[type]

        local_x = x % 16
        local_z = z % 16

        index = local_x + (local_z * 16)

        long_index = index // 7
        bit_index = index % 7

        long_value = data[long_index] & 0xFFFFFFFFFFFFFFFF
        value = (long_value >> (bit_index * 9)) & ((1 << 9) - 1)

        return value + min_y


class Region:
    """
    Represents a Minecraft region.

    Can be used to fetch all the chunks inside
    """

    _data: io.BytesIO
    _locations: bytes


    def __init__(
        self,
        file_path: Path
    ) -> None:
        
        with open(file_path, "rb") as f:
            self._data = io.BytesIO(f.read())

        self._data.seek(0)
        
        self._locations = self._data.read(4096)


    def _get_chunk_location(
        self,
        local_x: int,
        local_z: int
    ) -> Tuple[int, int]:
        
        index = local_x + (local_z * 32)
        offset = index * 4

        entry = self._locations[offset : offset + 4]

        sector_offset = struct.unpack(">I", b"\x00" + entry[:3])[0]
        sector_count = entry[3]

        return sector_offset, sector_count


    def get_chunk(
        self,
        chunk_x: int,
        chunk_z: int
    ) -> Optional[Chunk]:
        """
        Returns the chunk with the given coordinates (can also be relative to this region), if it exists
        """

        local_x = chunk_x % 32
        local_z = chunk_z % 32

        sector_offset, sector_count = self._get_chunk_location(local_x, local_z)

        if sector_offset == 0 or sector_count == 0:
            return # type: ignore

        self._data.seek(sector_offset * 4096)

        length = struct.unpack(">I", self._data.read(4))[0]
        compression_type = struct.unpack(">B", self._data.read(1))[0]

        data = self._data.read(length - 1)

        if compression_type == 1:
            data = gzip.decompress(data)

        elif compression_type == 2:
            data = zlib.decompress(data)

        else:
            raise NotImplementedError(f"Only zlib compression is supported, found {compression_type}")

        data = io.BytesIO(data) # type: ignore
        nbt = nbtlib.File.parse(data)

        return Chunk(nbt)


class WorldReader:
    """
    Main API class useful to fetch world data
    """


    _world_snapshot: WorldSnapshot
    _data_version: int
    _lock: threading.Lock


    def __init__(
        self,
        world_snapshot: WorldSnapshot
    ) -> None:
        
        self._world_snapshot = world_snapshot
        self._lock = threading.Lock()
        self._data_version = self.get_data_version()

    
    def get_data_version(self) -> int:

        level_dat = nbtlib.load(self._world_snapshot.world_path / "level.dat")
        return level_dat["Data"]["DataVersion"]


    @property
    def data_version(self) -> int:
        return self._data_version


    @property
    def overworld_regions_path(self) -> Path:
        return self._world_snapshot.world_path / "region"

    
    @property
    def nether_regions_path(self)-> Path:
        return self._world_snapshot.world_path / "DIM-1" / "region"

    
    @property
    def end_regions_path(self) -> Path:
        return self._world_snapshot.world_path / "DIM1" / "region"


    def get_region(
        self,
        region_x: int,
        region_z: int,
        dimension: Dimension = Dimension.OVERWORLD
    ) -> Optional[Region]:
        """
        Returns the region with the given coordinates in the given dimension, if it exists
        """

        with self._lock:

            file = get_region_filename(region_x, region_z)

            regions_path = {
                Dimension.OVERWORLD: self.overworld_regions_path,
                Dimension.NETHER: self.nether_regions_path,
                Dimension.END: self.end_regions_path
            }[dimension]
            region_path =  regions_path / file

            if region_path.exists():

                return Region(region_path)

        return None


    @overload
    def get_block(
        self,
        block_pos: Vec3d,
        dimension: Dimension = Dimension.OVERWORLD
    ) -> Optional[Block]:
        ...


    @overload
    def get_block(
        self,
        x: int,
        y: int,
        z: int,
        dimension: Dimension = Dimension.OVERWORLD
    ) -> Optional[Block]:
        ...

    
    def get_block(
        self,
        *args,
        **kwargs
    ) -> Optional[Block]:
        """
        Returns the block at the given coordinates and dimension, if it exists
        """

        if len(args) in [3, 4]:
            block_pos = Vec3d(*args[:3]).to_int()
        else:
            block_pos = args[0]

        if len(args) in [2,  4]:
            dimension = args[-1]
        else:
            dimension = Dimension.OVERWORLD

        if "dimension" in kwargs:

            assert len(args) not in [2, 4]
            assert len(kwargs) == 1

            dimension = kwargs["dimension"]
        
        cx, _cy, cz = chunk_coords(block_pos).as_tuple()

        chunk = self.get_chunk(cx, cz, dimension) # type: ignore

        if chunk is not None:
            return chunk.get_block(*block_pos.as_tuple()) # type: ignore

        return None
     

    def get_chunk(
        self,
        chunk_x: int,
        chunk_z: int,
        dimension: Dimension = Dimension.OVERWORLD
    ) -> Optional[Chunk]:
        """
        Returns the chunk at the given coordinates and the given dimension, if it exists
        """
        
        rx, rz = chunk_to_region(chunk_x, chunk_z)

        region = self.get_region(rx, rz, dimension)

        if region is not None:
            return region.get_chunk(chunk_x, chunk_z)

        return None


class CachedWorldReader(WorldReader):
    """
    WorldReader with a cache.

    Useful to fetch lots of data and terrain doesnt change
    """


    _region_cache: OrderedDict[Tuple[int, int, Dimension], Optional[Region]]
    _chunk_cache: OrderedDict[Tuple[int, int, Dimension], Optional[Chunk]]
    

    def __init__(
        self,
        world_snapshot: WorldSnapshot
    ) -> None:

        super().__init__(world_snapshot)

        self._region_cache = OrderedDict()
        self._chunk_cache = OrderedDict()


    @property
    def overworld(self) -> Overworld:
        """
        Overworld dimension
        """

        return Overworld(self)


    @property
    def nether(self) -> Nether:
        """
        Nether dimension
        """

        return Nether(self)


    @property
    def end(self) -> End:
        """
        End dimension
        """

        return End(self)


    def clear_cache(self) -> None:
        """
        Clears all the caches
        """

        self._region_cache.clear()
        self._chunk_cache.clear()


    def get_region(
        self,
        region_x: int,
        region_z: int,
        dimension: Dimension = Dimension.OVERWORLD
    ) -> Optional[Region]:
        """
        Returns the region with the given coordinates in the given dimension, if it exists
        """
        
        key = (region_x, region_z, dimension)

        if key in self._region_cache:

            self._region_cache.move_to_end(key)
            return self._region_cache[key]

        region = super().get_region(region_x, region_z, dimension)
        self._region_cache[key] = region

        if len(self._region_cache) > MAX_CACHED_REGIONS:
            self._region_cache.popitem(last=False)
        
        return region

    
    def get_chunk(
        self,
        chunk_x: int,
        chunk_z: int,
        dimension: Dimension = Dimension.OVERWORLD
    ) -> Optional[Chunk]:
        """
        Returns the chunk at the given coordinates and the given dimension, if it exists
        """
        
        key = (chunk_x, chunk_z, dimension)

        if key in self._chunk_cache:

            self._chunk_cache.move_to_end(key)
            return self._chunk_cache[key]

        chunk = super().get_chunk(chunk_x, chunk_z, dimension)
        self._chunk_cache[key] = chunk

        if len(self._chunk_cache) > MAX_CACHED_CHUNKS:
            self._chunk_cache.popitem(last=False)

        return chunk


class BaseSingleDimensionWorldReader(ABC):
    """
    Base class for a single-dimension world reader interfaces
    """

    DIMENSION: Dimension
    world_reader: CachedWorldReader


    def __init__(
        self,
        world_reader: CachedWorldReader
    ) -> None:
        
        self.world_reader = world_reader


    def get_region(
        self,
        region_x: int,
        region_z: int
    ) -> Optional[Region]:
        """
        Returns the region with the given coordinates in the given dimension, if it exists
        """

        return self.world_reader.get_region(region_x, region_z, self.DIMENSION)

    
    def get_chunk(
        self,
        chunk_x: int,
        chunk_z: int
    ) -> Optional[Chunk]:
        """
        Returns the chunk at the given coordinates and the given dimension, if it exists
        """

        return self.world_reader.get_chunk(chunk_x, chunk_z, self.DIMENSION)


    @overload
    def get_block(
        self,
        block_pos: Vec3d,
    ) -> Optional[Block]:
        ...


    @overload
    def get_block(
        self,
        x: int,
        y: int,
        z: int
    ) -> Optional[Block]:
        ...

    
    def get_block(
        self,
        *args,
        **kwargs
    ) -> Optional[Block]:
        """
        Returns the block at the given coordinates and dimension, if it exists
        """

        if "block_pos" in kwargs:

            block_pos = kwargs["block_pos"]
            assert isinstance(block_pos, Vec3d)
            return self.world_reader.get_block(block_pos, dimension=self.DIMENSION)

        if len(args) == 1:

            assert isinstance(args[0], Vec3d)
            return self.world_reader.get_block(args[0], dimension=self.DIMENSION)
        
        return self.world_reader.get_block(int(args[0]), int(args[1]), int(args[2]), dimension=self.DIMENSION)


class Overworld(BaseSingleDimensionWorldReader):
    DIMENSION: Dimension = Dimension.OVERWORLD


class Nether(BaseSingleDimensionWorldReader):
    DIMENSION: Dimension = Dimension.NETHER


class End(BaseSingleDimensionWorldReader):
    DIMENSION: Dimension = Dimension.END