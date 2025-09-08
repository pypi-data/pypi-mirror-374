from __future__ import annotations
from dataclasses import dataclass
import enum


def rgb_to_hex(red: int, green: int, blue: int, bit_depth: int = 8) -> int:
    hex = 0
    for i, channel in enumerate((blue, green, red)):
        hex |= channel << (i * bit_depth)
    return hex


def hex_to_rgb(hex: int | str, bit_depth: int = 8) -> tuple[int, int, int]:
    if isinstance(hex, str):
        hex = int(hex, 16)
    mask = (1 << bit_depth) - 1
    return tuple([hex >> (i * bit_depth) & mask for i in range(2, -1, -1)])


@dataclass(frozen=True, order=True)
class Color:
    id: int
    label: str
    hex: int
    premium: bool

    @property
    def rgb(self) -> tuple[int, int, int]:
        return hex_to_rgb(self.hex)

    def __str__(self) -> str:
        return self.label

    def __repr__(self) -> str:
        return repr(str(self))


class PaletteColor(Color, enum.Enum):
    BLACK =             1, "Black",            0x000000, False
    DARK_GRAY =         2, "Dark Gray",        0x3c3c3c, False
    GRAY =              3, "Gray",             0x787878, False
    MEDIUM_GRAY =      32, "Medium Gray",      0xaaaaaa, True
    LIGHT_GRAY =        4, "Light Gray",       0xd2d2d2, False
    WHITE =             5, "White",            0xffffff, False
    DEEP_RED =          6, "Deep Red",         0x600018, False
    DARK_RED =         33, "Dark Red",         0xa50e1e, True
    RED =               7, "Red",              0xed1c24, False
    LIGHT_RED =        34, "Light Red",        0xfa8072, True
    DARK_ORANGE =      35, "Dark Orange",      0xe45c1a, True
    ORANGE =            8, "Orange",           0xff7f27, False
    GOLD =              9, "Gold",             0xf6aa09, False
    YELLOW =           10, "Yellow",           0xf9dd3b, False
    LIGHT_YELLOW =     11, "Light Yellow",     0xfffabc, False
    DARK_GOLDENROD =   37, "Dark Goldenrod",   0x9c8431, True
    GOLDENROD =        38, "Goldenrod",        0xc5ad31, True
    LIGHT_GOLDENROD =  39, "Light Goldenrod",  0xe8d45f, True
    DARK_OLIVE =       40, "Dark Olive",       0x4a6b3a, True
    OLIVE =            41, "Olive",            0x5a944a, True
    LIGHT_OLIVE =      42, "Light Olive",      0x84c573, True
    DARK_GREEN =       12, "Dark Green",       0x0eb968, False
    GREEN =            13, "Green",            0x13e67b, False
    LIGHT_GREEN =      14, "Light Green",      0x87ff5e, False
    DARK_TEAL =        15, "Dark Teal",        0x0c816e, False
    TEAL =             16, "Teal",             0x10aea6, False
    LIGHT_TEAL =       17, "Light Teal",       0x13e1be, False
    DARK_CYAN =        43, "Dark Cyan",        0x0f799f, True
    CYAN =             20, "Cyan",             0x60f7f2, False
    LIGHT_CYAN =       44, "Light Cyan",       0xbbfaf2, True
    DARK_BLUE =        18, "Dark Blue",        0x28509e, False
    BLUE =             19, "Blue",             0x4093e4, False
    LIGHT_BLUE =       45, "Light Blue",       0x7dc7ff, True
    DARK_INDIGO =      46, "Dark Indigo",      0x4d31b8, True
    INDIGO =           21, "Indigo",           0x6b50f6, False
    LIGHT_INDIGO =     22, "Light Indigo",     0x99b1fb, False
    DARK_SLATE_BLUE =  47, "Dark Slate Blue",  0x4a4284, True
    SLATE_BLUE =       48, "Slate Blue",       0x7a71c4, True
    LIGHT_SLATE_BLUE = 49, "Light Slate Blue", 0xb5aef1, True
    DARK_PURPLE =      23, "Dark Purple",      0x780c99, False
    PURPLE =           24, "Purple",           0xaa38b9, False
    LIGHT_PURPLE =     25, "Light Purple",     0xe09ff9, False
    DARK_PINK =        26, "Dark Pink",        0xcb007a, False
    PINK =             27, "Pink",             0xec1f80, False
    LIGHT_PINK =       28, "Light Pink",       0xf38da9, False
    DARK_PEACH =       53, "Dark Peach",       0x9b5249, True
    PEACH =            54, "Peach",            0xd18078, True
    LIGHT_PEACH =      55, "Light Peach",      0xfab6a4, True
    DARK_BROWN =       29, "Dark Brown",       0x684634, False
    BROWN =            30, "Brown",            0x95682a, False
    LIGHT_BROWN =      50, "Light Brown",      0xdba463, True
    DARK_TAN =         56, "Dark Tan",         0x7b6352, True
    TAN =              57, "Tan",              0x9c846b, True
    LIGHT_TAN =        36, "Light Tan",        0xd6b594, True
    DARK_BEIGE =       51, "Dark Beige",       0xd18051, True
    BEIGE =            31, "Beige",            0xf8b277, False
    LIGHT_BEIGE =      52, "Light Beige",      0xffc5a5, True
    DARK_STONE =       61, "Dark Stone",       0x6d643f, True
    STONE =            62, "Stone",            0x948c6b, True
    LIGHT_STONE =      63, "Light Stone",      0xcdc59e, True
    DARK_SLATE =       58, "Dark Slate",       0x333941, True
    SLATE =            59, "Slate",            0x6d758d, True
    LIGHT_SLATE =      60, "Light Slate",      0xb3b9d1, True
    TRANSPARENT =       0, "Transparent",      0xdeface, False

    @classmethod
    def from_hex(cls, hex: int | str) -> PaletteColor:
        if isinstance(hex, str):
            hex = int(hex, 16)
        for color in cls:
            if color.hex == hex:
                return color
        raise NotImplementedError(
            f"No palette color available for hex code {hex:06x}")

    @classmethod
    def from_rgba(
        cls,
        red: int,
        green: int,
        blue: int,
        alpha: int = 255,
    ) -> PaletteColor:
        if not alpha:
            return cls.TRANSPARENT
        try:
            return cls.from_hex(rgb_to_hex(red, green, blue, bit_depth=8))
        except NotImplementedError as exc:
            rgba = (red, green, blue, alpha)
            raise NotImplementedError(
                f"No palette color available for RGBA tuple {rgba}") from exc

    @classmethod
    def from_id(cls, id: int) -> PaletteColor:
        for color in cls:
            if color.id == id:
                return color
        raise NotImplementedError(
            f"No palette color available for ID {id}")
