import itertools
import numpy as np
from PIL import Image
import time

import canvas
from colors import PaletteColor
from image_processing import standardize_color_palette


COLOR_ICON_BITS: dict[PaletteColor, int] = {
    PaletteColor.BLACK:             4897444,
    PaletteColor.DARK_GRAY:         4756004,
    PaletteColor.GRAY:             15241774,
    PaletteColor.MEDIUM_GRAY:      31850982,
    PaletteColor.LIGHT_GRAY:       11065002,
    PaletteColor.WHITE:            15269550,
    PaletteColor.DEEP_RED:         33209205,
    PaletteColor.DARK_RED:         19267878,
    PaletteColor.RED:              15728622,
    PaletteColor.LIGHT_RED:        16236308,
    PaletteColor.DARK_ORANGE:      33481548,
    PaletteColor.ORANGE:           15658734,
    PaletteColor.GOLD:             33226431,
    PaletteColor.YELLOW:           33391295,
    PaletteColor.LIGHT_YELLOW:     32641727,
    PaletteColor.DARK_GOLDENROD:   22708917,
    PaletteColor.GOLDENROD:        14352822,
    PaletteColor.LIGHT_GOLDENROD:   7847326,
    PaletteColor.DARK_OLIVE:        7652956,
    PaletteColor.OLIVE:            22501038,
    PaletteColor.LIGHT_OLIVE:      28457653,
    PaletteColor.DARK_GREEN:       15589098,
    PaletteColor.GREEN:            11516906,
    PaletteColor.LIGHT_GREEN:       9760338,
    PaletteColor.DARK_TEAL:        15399560,
    PaletteColor.TEAL:              4685802,
    PaletteColor.LIGHT_TEAL:       15587182,
    PaletteColor.DARK_CYAN:         9179234,
    PaletteColor.CYAN:             29206876,
    PaletteColor.LIGHT_CYAN:       30349539,
    PaletteColor.DARK_BLUE:         3570904,
    PaletteColor.BLUE:             15259182,
    PaletteColor.LIGHT_BLUE:        4685269,
    PaletteColor.DARK_INDIGO:      18295249,
    PaletteColor.INDIGO:           29224831,
    PaletteColor.LIGHT_INDIGO:     21427311,
    PaletteColor.DARK_SLATE_BLUE:  26843769,
    PaletteColor.SLATE_BLUE:       24483191,
    PaletteColor.LIGHT_SLATE_BLUE:  5211003,
    PaletteColor.DARK_PURPLE:      22511061,
    PaletteColor.PURPLE:           15161013,
    PaletteColor.LIGHT_PURPLE:      4667844,
    PaletteColor.DARK_PINK:        11392452,
    PaletteColor.PINK:             11375466,
    PaletteColor.LIGHT_PINK:        6812424,
    PaletteColor.DARK_PEACH:       14829567,
    PaletteColor.PEACH:            17971345,
    PaletteColor.LIGHT_PEACH:      28873275,
    PaletteColor.DARK_BROWN:        5225454,
    PaletteColor.BROWN:            29197179,
    PaletteColor.LIGHT_BROWN:       4681156,
    PaletteColor.DARK_TAN:         21392581,
    PaletteColor.TAN:               7460636,
    PaletteColor.LIGHT_TAN:        23013877,
    PaletteColor.DARK_BEIGE:       29010254,
    PaletteColor.BEIGE:            18285009,
    PaletteColor.LIGHT_BEIGE:      18846257,
    PaletteColor.DARK_STONE:       21825364,
    PaletteColor.STONE:            29017787,
    PaletteColor.LIGHT_STONE:       4357252,
    PaletteColor.DARK_SLATE:       23057550,
    PaletteColor.SLATE:            26880179,
    PaletteColor.LIGHT_SLATE:       5242308,
    PaletteColor.TRANSPARENT:      15237450,
}


def get_rgb_color_map() -> dict[tuple[int, int, int], PaletteColor]:
    return {color.rgb: color for color in PaletteColor}


def get_rgb_palette(
    sort_by: str = "id",
    incl_trans: bool = False,
    incl_alpha: bool = False,
    flatten: bool = False,
) -> list[tuple[int, ...]] | list[int]:
    palette = []

    if sort_by == "palette":
        sorter = lambda color: tuple(PaletteColor).index(color)
    else:
        sorter = lambda color: getattr(color, sort_by)

    for color in sorted(PaletteColor, key=sorter):
        if color == PaletteColor.TRANSPARENT:
            alpha = 0
            if not incl_trans:
                continue
        else:
            alpha = 255

        color_tuple = color.rgb
        if incl_alpha:
            color_tuple = tuple(list(color_tuple) + [alpha])

        if flatten:
            palette.extend(color_tuple)
        else:
            palette.append(color_tuple)

    return palette


def get_color_icon(color: PaletteColor) -> Image.Image:
    n_pixels: int = 5
    bitmap = COLOR_ICON_BITS[color]
    bits = [bitmap >> i & 0b1 for i in range(n_pixels * n_pixels)]
    array = np.array(bits, dtype=np.uint8).reshape((n_pixels, n_pixels))
    image = Image.fromarray(array)
    image.putpalette([0, 0, 0] + list(color.rgb))
    image.info["transparency"] = 0
    return image


def download_area_image(
    origin: canvas.Pixel,
    width: int,
    height: int,
    sleep_time: float = 1.,
) -> Image.Image:
    """Load all needed tile images from the backend and create an image of the
    specified area.

    Returns:
        Image.Image: Indexed image with the Wplace color palette (63 solid
            colors + full transparency).
    """
    # TODO: Implement incremental download / save to handle large areas
    # TODO: Implement option to use already downloaded tile images
    start_tile = origin.tile
    x_start, y_start = origin.tile_pixel

    n_cols = 1 + (x_start + width - 1) // canvas.N_TILE_PIXELS_X
    n_rows = 1 + (y_start + height - 1) // canvas.N_TILE_PIXELS_Y
    n_tiles = n_cols * n_rows

    # init empty array to stitch tiles
    trans_index = PaletteColor.TRANSPARENT.id
    array_width = n_cols * canvas.N_TILE_PIXELS_X
    array_height = n_rows * canvas.N_TILE_PIXELS_Y
    array = np.ones((array_height, array_width), dtype=np.uint8) * trans_index

    for i, (col, row) in enumerate(itertools.product(range(n_cols), range(n_rows))):
        try:
            tile = start_tile + (col, row)
        except ValueError:
            # TODO: Handle out-of-bounds better
            continue
        tile_image = tile.download_image(save=False)
        if tile_image is None:
            continue
        tile_image = standardize_color_palette(tile_image)
        x0 = col * canvas.N_TILE_PIXELS_X
        x1 = x0 + canvas.N_TILE_PIXELS_X
        y0 = row * canvas.N_TILE_PIXELS_Y
        y1 = y0 + canvas.N_TILE_PIXELS_Y
        array[y0:y1, x0:x1] = np.array(tile_image, dtype=np.uint8)
        del tile_image
        if i < n_tiles - 1:
            time.sleep(sleep_time)

    cutout = array[y_start:y_start + height, x_start:x_start + width]
    image = Image.fromarray(cutout)
    image.putpalette(PaletteColor.rgb_palette(incl_trans=True, flatten=True))
    image.info["transparency"] = trans_index
    return image


def decode_unlocked_premium_colors(bit_pattern: int) -> tuple[PaletteColor, ...]:
    """Extract list of unlocked premium colors from `extraColorsBitmap`."""
    colors = []
    for color in PaletteColor:
        if not color.premium:
            continue
        if (bit_pattern >> (color.id - 32)) & 0b1:
            colors.append(color)
    return tuple(colors)
