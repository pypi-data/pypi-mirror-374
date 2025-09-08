from __future__ import annotations
from dataclasses import dataclass
from pyproj import CRS, Transformer
from rasterio.transform import from_bounds, rowcol, xy
from typing import Iterator


# setup of the pixel canvas
N_TILES_X: int = 2048
N_TILES_Y: int = 2048
N_TILE_PIXELS_X: int = 1000
N_TILE_PIXELS_Y: int = 1000
N_PIXELS_X: int = N_TILES_X * N_TILE_PIXELS_X
N_PIXELS_Y: int = N_TILES_Y * N_TILE_PIXELS_Y
N_REGION_PIXELS_X: int = 4000
N_REGION_PIXELS_Y: int = 4000
N_REGIONS_X: int = N_PIXELS_X // N_REGION_PIXELS_X
N_REGIONS_Y: int = N_PIXELS_Y // N_REGION_PIXELS_Y

# used coordinate reference systems
EPSG_3857 = CRS.from_epsg(3857) # Pseudo-Mercator
EPSG_4326 = CRS.from_epsg(4326) # longitude / latitude (WGS84)

# transformations between Pseudo-Mercator and WGS84
FROM_LONLAT = Transformer.from_crs(EPSG_4326, EPSG_3857, always_xy=True)
TO_LONLAT = Transformer.from_crs(EPSG_3857, EPSG_4326, always_xy=True)

# WGS84 bounds of the canvas from https://maps.wplace.live/planet
LON_WEST: float = -180.
LON_EAST: float =  180.
LAT_NORTH: float =  85.05113
LAT_SOUTH: float = -85.05113

# canvas bounds in EPSG:3857
WEST, NORTH = FROM_LONLAT.transform(xx=LON_WEST, yy=LAT_NORTH)
EAST, SOUTH = FROM_LONLAT.transform(xx=LON_EAST, yy=LAT_SOUTH)

# transformation between pixel coordinated and EPSG:3857
PIXEL_TRAFO = from_bounds(
    west=WEST,
    north=NORTH,
    east=EAST,
    south=SOUTH,
    width=N_PIXELS_X,
    height=N_PIXELS_Y,
)

# used (backend) URLs
WPLACE_URL: str = "https://wplace.live"
BACKEND_URL: str = "https://backend.wplace.live"
TILE_BASE_URL: str = f"{BACKEND_URL}/files/s0/tiles"
PIXEL_BASE_URL: str = f"{BACKEND_URL}/s0/pixel"


def pixel_to_lonlat(col: int, row: int) -> tuple[float, float]:
    """Return the WGS84 longitude and latitude of a pixel on the Wplace
    canvas.
    """
    x, y = xy(PIXEL_TRAFO, row, col)
    return TO_LONLAT.transform(x, y)


def lonlat_to_pixel(lon: float, lat: float) -> tuple[int, int]:
    """Return the pixel coordinate on the Wplace canvas corresponding to the
    given WGS84 longitude and latitude.
    """
    x, y = FROM_LONLAT.transform(lon, lat)
    row, col = rowcol(PIXEL_TRAFO, x, y)
    return col.item(), row.item()


# TODO: Refactor Region, Tile, and Pixel to use the same parent class
@dataclass(frozen=True, order=True)
class Region:
    """A 4000 x 4000 pixels region on the Wplace canvas."""
    x: int
    y: int

    def __post_init__(self) -> None:
        if not 0 <= self.x < N_REGIONS_X:
            raise ValueError(
                f"x coordinate has to be within [{0},"
                f" {N_REGIONS_X - 1}], got {self.x}")
        if not 0 <= self.y < N_REGIONS_Y:
            raise ValueError(
                f"y coordinate has to be within [{0},"
                f" {N_REGIONS_Y - 1}], got {self.y}")

    def __iter__(self) -> Iterator[int]:
        yield from (self.x, self.y)

    def __add__(self, other) -> Tile:
        x, y = other
        return type(self)(
            x=(self.x + x) % N_REGIONS_X,
            y=self.y + y,
        )

    def __sub__(self, other) -> Tile:
        x, y = other
        return type(self)(
            x=(self.x - x) % N_REGIONS_X,
            y=self.y - y,
        )

    @property
    def origin(self) -> Pixel:
        """Return the most north-west pixel of the region."""
        return Pixel(
            x=self.x * N_REGION_PIXELS_X,
            y=self.y * N_REGION_PIXELS_Y,
        )


@dataclass(frozen=True, order=True)
class Tile:
    """A 1000 x 1000 pixels tile on the Wplace canvas."""
    x: int
    y: int

    def __post_init__(self) -> None:
        if not 0 <= self.x < N_TILES_X:
            raise ValueError(
                f"x coordinate has to be within [{0},"
                f" {N_TILES_X - 1}], got {self.x}")
        if not 0 <= self.y < N_TILES_Y:
            raise ValueError(
                f"y coordinate has to be within [{0},"
                f" {N_TILES_Y - 1}], got {self.y}")

    def __iter__(self) -> Iterator[int]:
        yield from (self.x, self.y)

    def __add__(self, other) -> Tile:
        x, y = other
        return type(self)(
            x=(self.x + x) % N_TILES_X,
            y=self.y + y,
        )

    def __sub__(self, other) -> Tile:
        x, y = other
        return type(self)(
            x=(self.x - x) % N_TILES_X,
            y=self.y - y,
        )

    @property
    def origin(self) -> Pixel:
        """Return the most north-west pixel of the tile."""
        return Pixel(
            x=self.x * N_TILE_PIXELS_X,
            y=self.y * N_TILE_PIXELS_Y,
        )

    @property
    def region(self) -> Region:
        """Return the canvas region that contains the tile."""
        return self.origin.region

    @property
    def url(self) -> str:
        """Return the backend URL of the tile image."""
        return f"{TILE_BASE_URL}/{self.x}/{self.y}.png"


@dataclass(frozen=True, order=True)
class Pixel:
    """A pixel on the Wplace canvas."""
    x: int
    y: int

    def __post_init__(self) -> None:
        if not 0 <= self.x < N_PIXELS_X:
            raise ValueError(
                f"x coordinate has to be within [{0},"
                f" {N_PIXELS_X - 1}], got {self.x}")
        if not 0 <= self.y < N_PIXELS_Y:
            raise ValueError(
                f"y coordinate has to be within [{0},"
                f" {N_PIXELS_Y - 1}], got {self.y}")

    def __iter__(self) -> Iterator[int]:
        yield from (self.x, self.y)

    def __add__(self, other) -> Pixel:
        x, y = other
        return type(self)(
            x=(self.x + x) % N_PIXELS_X,
            y=self.y + y,
        )

    def __sub__(self, other) -> Pixel:
        x, y = other
        return type(self)(
            x=(self.x - x) % N_PIXELS_X,
            y=self.y - y,
        )

    @classmethod
    def from_tile(
        cls,
        tile: Tile,
        pixel_x: int = 0,
        pixel_y: int = 0,
    ) -> Pixel:
        if not 0 <= pixel_x < N_TILE_PIXELS_X:
            raise ValueError(
                f"x coordinate within tile has to be within [{0},"
                f" {N_TILE_PIXELS_X - 1}], got {pixel_x}")
        if not 0 <= pixel_y < N_TILE_PIXELS_Y:
            raise ValueError(
                f"y coordinate within tile has to be within [{0},"
                f" {N_TILE_PIXELS_Y - 1}], got {pixel_y}")
        return tile.origin + (pixel_x, pixel_y)

    @classmethod
    def from_region(
        cls,
        region: Region,
        pixel_x: int = 0,
        pixel_y: int = 0,
    ) -> Pixel:
        if not 0 <= pixel_x < N_REGION_PIXELS_X:
            raise ValueError(
                f"x coordinate within region has to be within [{0},"
                f" {N_REGION_PIXELS_X - 1}], got {pixel_x}")
        if not 0 <= pixel_y < N_REGION_PIXELS_Y:
            raise ValueError(
                f"y coordinate within region has to be within [{0},"
                f" {N_REGION_PIXELS_Y - 1}], got {pixel_y}")
        return region.origin + (pixel_x, pixel_y)

    @classmethod
    def from_lonlat(cls, longitude: float, latitude: float) -> Pixel:
        x, y = lonlat_to_pixel(lon=longitude, lat=latitude)
        return cls(x=x, y=y)

    @property
    def tile(self) -> Tile:
        """Return the canvas tile that contains the pixel."""
        return Tile(
            x=self.x // N_TILE_PIXELS_X,
            y=self.y // N_TILE_PIXELS_Y,
        )

    @property
    def tile_pixel(self) -> tuple[int, int]:
        """Return coordinates of the pixel within its canvas tile."""
        return (
            self.x % N_TILE_PIXELS_X,
            self.y % N_TILE_PIXELS_Y,
        )

    @property
    def region(self) -> Region:
        """Return the canvas region that contains the pixel."""
        return Region(
            x=self.x // N_REGION_PIXELS_X,
            y=self.y // N_REGION_PIXELS_Y,
        )

    @property
    def region_pixel(self) -> tuple[int, int]:
        """Return coordinates of the pixel within its canvas region."""
        return (
            self.x % N_REGION_PIXELS_X,
            self.y % N_REGION_PIXELS_Y,
        )

    @property
    def lonlat(self) -> tuple[float, float]:
        """Return the WGS84 longitude and latitude of the pixel."""
        return pixel_to_lonlat(col=self.x, row=self.y)

    @property
    def url(self) -> str:
        """Return the backend URL used to get information about the pixel."""
        tile_x, tile_y = self.tile
        pixel_x, pixel_y = self.tile_pixel
        return f"{PIXEL_BASE_URL}/{tile_x}/{tile_y}?x={pixel_x}&y={pixel_y}"

    def link(
        self,
        select: bool = False,
        zoom: float | None = None,
    ) -> str:
        """Return link that navigates to the pixel on the Wplace canvas."""
        lon, lat = self.lonlat
        url = f"{WPLACE_URL}/?lat={lat}&lng={lon}"
        if zoom is not None:
            url += f"&zoom={zoom}"
        if select:
            url += "&select=0"
        return url
