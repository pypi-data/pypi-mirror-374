from math import ceil


def tiles(
    tile_x=None,
    tile_y=None,
    area_x=None,
    area_y=None,
    gap_x=None,
    gap_y=None,
):
    x = ceil(area_x / (tile_x + gap_x))
    y = ceil(area_y / (tile_y + gap_y))
    return x * y


if __name__ == "__main__":
    print(ceil(8/8))
    print(tiles(30, 30, 300, 300, 10, 10))
