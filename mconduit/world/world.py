from typing import Optional, Tuple, Dict, List
from pathlib import Path
import threading
import shutil
import nbtlib
import struct
import math
import zlib
import gzip
import io

from ..utils.coords import chunk_coords, iter_coord
from ..server_api import Properties # NOTE: This will become standard at some point
from .._types.vec3d import Vec3d
from ..enums import Dimension
from ..server import Server


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


class Block:
    ...

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

    __data: nbtlib.Base
    __sections: Dict[int, SubChunk]


    def __init__(
        self,
        nbt: nbtlib.Base
    ) -> None:
        
        self.__data = nbt
        self.__sections = {}
        
        for section in self.__data.get("sections", []):

            y = int(section["Y"])
            self.__sections[y] = SubChunk(section)
    

    @property
    def x(self) -> int:
        """
        Chunk x coordinate
        """

        return self.__data["xPos"]


    @property
    def z(self) -> int:
        """
        Chunk z coordinate
        """

        return self.__data["zPos"]

    
    def get_block(
        self,
        block_coords: Vec3d
    ) -> Block:
        """
        Returns the block at the given coords (they can also be relative to this chunk)
        """

        section_y = int(block_coords.y // 16)
        section = self.__sections[section_y]

        palette = section.palette
        data = section.data

        if data is None:
            return palette[0]

        local_x = block_coords.x % 16
        local_y = block_coords.y % 16
        local_z = block_coords.z % 16

        index = (local_y * 16 + local_z) * 16 + local_x

        bits_per_block = max(4, math.ceil(math.log2(len(palette))))
        blocks_per_long = 64 // bits_per_block

        long_index = index // blocks_per_long
        bit_index = (index % blocks_per_long) * bits_per_block

        if long_index >= len(data):
            return palette[0]
                
        value = (data[long_index] >> bit_index) & ((1 << bits_per_block) - 1)

        return palette[int(value)]
            
    
    def get_height(
        self,
        x: int,
        z: int,
        type: str = "MOTION_BLOCKING", # TODO: This might be replaced with an Enum
        min_y: int = -64
    ) -> int:
        """
        Returns the highest Y on the given x and y coordinates (they can also be relative to this chunk)
        """
        
        data = self.__data.get("Heightmaps")[type]

        local_x = x % 16
        local_z = z % 16

        index = local_x + (local_z * 16)

        entries_per_long = 64 // 9

        long_index = index // entries_per_long
        bit_index = index % entries_per_long

        value = (data[long_index] >> bit_index) & ((1 << 9 ) - 1)

        return value + min_y


class Region:
    """
    Represents a Minecraft region.

    Can be used to fetch all the chunks inside
    """

    __data: io.BytesIO
    __locations: bytes


    def __init__(
        self,
        file_path: Path
    ) -> None:
        
        with open(file_path, "rb") as f:
            self.__data = io.BytesIO(f.read())

        self.__data.seek(0)
        
        self.__locations = self.__data.read(4096)


    def _get_chunk_location(
        self,
        local_x: int,
        local_z: int
    ) -> Tuple[int, int]:
        
        index = local_x + (local_z * 32)
        offset = index * 4

        entry = self.__locations[offset : offset + 4]

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

        self.__data.seek(sector_offset * 4096)

        length = struct.unpack(">I", self.__data.read(4))[0]
        compression_type = struct.unpack(">B", self.__data.read(1))[0]

        data = self.__data.read(length - 1)

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

    __data_version: int
    __world_path: Path
    __lock: threading.Lock


    def __init__(
        self,
        server: Server
    ) -> None:
        
        self.server = server
        self.__lock = threading.Lock()
        self.__world_path = self.get_world_path()
        self.__data_version = self.get_data_version()

    
    def get_data_version(self) -> int:

        level_dat = nbtlib.load(self.world_path / "level.dat")
        return level_dat["Data"]["DataVersion"]


    def get_world_path(self) -> Path:
        return self.server.path / Properties(server=self.server).get("level-name", "world")


    @property
    def data_version(self) -> int:
        return self.__data_version
    

    @property
    def world_path(self) -> Path:
        return self.__world_path

    
    @property
    def nether_regions_path(self)-> Path:
        return self.__world_path / "DIM-1" / "region"

    
    @property
    def end_regions_path(self) -> Path:
        return self.__world_path / "DIM1" / "region"

    
    @property
    def regions_path(self) -> Path:
        return self.__world_path / "region"

    
    @property
    def temp_region_path(self) -> Path:
        return self.server.path / "temp-regions"

    
    def _copy_region(
        self,
        region_file: Path
    ) -> Path:
        """
        Copies the region into a separate folder to avoid concurrency errors with Minecraft.

        Returns the new path where the region is copied and should be read
        """

        new_path = self.temp_region_path
        dim = region_file.parent.parent.name
        
        if dim in ["DIM-1", "DIM1"]:
            new_path = new_path / dim
        
        new_path.mkdir(parents=True, exist_ok=True)
        new_path = new_path / region_file.name
        
        shutil.copy2(region_file, new_path)
        
        return new_path


    def get_region(
        self,
        region_x: int,
        region_z: int,
        dimension: Dimension = Dimension.Overworld
    ) -> Optional[Region]:
        """
        Returns the region with the given coordinates in the given dimension, if it exists
        """
        
        with self.__lock:

            file = get_region_filename(region_x, region_z)

            regions_path = {
                Dimension.Overworld: self.regions_path,
                Dimension.Nether: self.nether_regions_path,
                Dimension.End: self.end_regions_path
            }[dimension]
            region_path =  regions_path / file

            if region_path.exists():

                read_path = self._copy_region(region_path)

                return Region(read_path)


    def get_regions(
        self,
        start_x: int,
        start_z: int,
        end_x: int,
        end_z: int,
        dimension: Dimension = Dimension.Overworld
    ) -> List[Region]:
        """
        Returns a list of all the regions between the given coordinates.

        If a region does not exists is skipped
        """
        
        regions = []

        for x in iter_coord(start_x, end_x):

            for z in iter_coord(start_z, end_z):

                region = self.get_region(x, z, dimension)

                if region is not None:
                    regions.append(region)

        return regions


    def get_block(
        self,
        block_pos: Vec3d,
        dimension: Dimension = Dimension.Overworld
    ) -> Optional[Block]:
        """
        Returns the block at the given coordinates and dimension, if it exists
        """
        
        cx, _cy, cz = chunk_coords(block_pos).as_tuple()

        chunk = self.get_chunk(cx, cz, dimension) # type: ignore

        if chunk is not None:
            return chunk.get_block(block_pos)
     

    def get_chunk(
        self,
        chunk_x: int,
        chunk_z: int,
        dimension: Dimension = Dimension.Overworld
    ) -> Optional[Chunk]:
        """
        Returns the chunk at the given coordinates and the given dimension, if it exists
        """
        
        rx, rz = chunk_to_region(chunk_x, chunk_z)

        region = self.get_region(rx, rz, dimension)

        if region is not None:
            return region.get_chunk(chunk_x, chunk_z)


    def get_chunks(
        self,
        start_x: int,
        start_z: int,
        end_x: int,
        end_z: int,
        dimension: Dimension = Dimension.Overworld
    ) -> List[Chunk]:
        """
        Returns a list with all the chunks between the given coordinates.

        If a chunk does not exists is skipped
        """

        chunks = []
        
        for x in iter_coord(start_x, end_x):

            for z in iter_coord(start_z, end_z):

                chunk = self.get_chunk(x, z, dimension)

                if chunk is not None:
                    chunks.append(chunk)

        return chunks
        

    def get_sub_chunk(
        self,
        sub_chunk_pos: Vec3d,
        dimension: Dimension = Dimension.Overworld
    ) -> Optional[SubChunk]:
        raise NotImplementedError

    def get_sub_chunks(
        self,
        start: Vec3d,
        end: Vec3d,
        dimension: Dimension = Dimension.Overworld
    ) -> List[SubChunk]:
        raise NotImplementedError

    def get_blocks(
        self,
        start: Vec3d,
        end: Vec3d,
        dimension: Dimension = Dimension.Overworld
    ) -> List[Block]:
        
        blocks = [] # type: ignore
        x1, _y1, z1 = chunk_coords(start).as_tuple()
        x2, _y2, z2 = chunk_coords(end).as_tuple()
        
        raise NotImplementedError

        chunks = self.get_chunks(x1, z1, x2, z2, dimension)
        
        for chunk in chunks:

            cx, cz = chunk.x, chunk.z

        for x in iter_coord(start.x):

            cx = x // 16

            for z in iter_coord(start.z):
                
                cz = z // 16

                for y in iter_coord(start.y):

                    block = self.get_block(x, y, z, dimension)

                    if block is not None:
                        blocks.append(block)

        return blocks


class CachedWorldReader(WorldReader):
    """
    WorldReader with a cache.

    Useful to fetch lots of data and terrain doesnt change
    """


    __region_cache: Dict[Tuple[int, int, Dimension], Optional[Region]]
    __chunk_cache: Dict[Tuple[int, int, Dimension], Optional[Chunk]]
    __block_cache: Dict[Tuple[Vec3d, Dimension], Optional[Block]]


    def __init__(
        self,
        server: Server
    ) -> None:

        super().__init__(server)

        self.__region_cache = {}
        self.__chunk_cache = {}
        self.__block_cache = {}


    def clean_cache(self) -> None:
        """
        Clears all the caches
        """

        self.__region_cache = {}
        self.__chunk_cache = {}
        self.__block_cache = {}


    def get_region(
        self,
        region_x: int,
        region_z: int,
        dimension: Dimension = Dimension.Overworld
    ) -> Region | None:

        if (region_x, region_z, dimension) in self.__region_cache:
            return self.__region_cache[(region_x, region_z, dimension)]

        region = super().get_region(region_x, region_z, dimension)
        self.__region_cache[(region_x, region_z, dimension)] = region

        return region

    
    def get_chunk(
        self,
        chunk_x: int,
        chunk_z: int,
        dimension: Dimension = Dimension.Overworld
    ) -> Chunk | None:

        if (chunk_x, chunk_z, dimension) in self.__chunk_cache:
            return self.__chunk_cache[(chunk_x, chunk_z, dimension)]

        chunk = super().get_chunk(chunk_x, chunk_z, dimension)
        self.__chunk_cache[(chunk_x, chunk_z, dimension)] = chunk

        return chunk

    
    def get_block(
        self,
        block_pos: Vec3d,
        dimension: Dimension = Dimension.Overworld
    ) -> Block | None:

        if (block_pos, dimension) in self.__block_cache:
            return self.__block_cache[(block_pos, dimension)]

        block = super().get_block(block_pos, dimension)
        self.__block_cache[(block_pos, dimension)] = block

        return block