from pyodide.http import pyfetch  # pyright: ignore[reportMissingImports]

from enum import Enum
from math import pi

__all__ = [
    "NODE",
    "MAP",
    "get_map_layout",
    #
    "ROOM_TYPES",
    "get_gallery_room",
]

NODE = tuple[bool, bool, bool, bool]
MAP = list[list[NODE | None]]


async def get_map_layout() -> MAP:
    r = await pyfetch("./assets/map.txt")
    text = await r.text()
    data = [i for i in text.split("\n") if i]

    # (x, y) = (0, 0) is top left corner
    output: MAP = [[] for _ in range(0, len(data), 2)]

    for y in range(0, len(data), 2):
        for x in range(0, len(data[y]), 4):
            if data[y][x] != "x":
                output[y // 2].append(None)
                continue

            north = False
            if (y - 1 > 0) and (data[y - 1][x] == "|"):
                north = True

            east = False
            if (x + 2 < len(data[y])) and (data[y][x + 2] == "-"):
                east = True

            south = False
            if (y + 1 < len(data)) and (data[y + 1][x] == "|"):
                south = True

            west = False
            if (x - 2 > 0) and (data[y][x - 2] == "-"):
                west = True

            output[y // 2].append((north, east, south, west))

    return output


class ROOM_TYPES(Enum):
    _1 = "1"
    _2s = "2s"
    _2c = "2c"
    _3 = "3"
    _4 = "4"


def get_gallery_room(
    x: int,
    y: int,
    layout: MAP,
) -> tuple[ROOM_TYPES, float]:
    node = layout[y][x]
    assert node is not None
    north, east, south, west = node

    match (north, east, south, west):
        # 4 exits
        case z if all(z):
            return ROOM_TYPES._4, 0
        # no exit
        case z if not any(z):
            assert False

        # 1 exit
        case z if sum(z) == 1:
            for idx, i in enumerate(z):
                if i:
                    break
            else:
                assert False
            return ROOM_TYPES._1, (pi / 2 * ((-idx + 3) % 4))

        # 2 exits
        # straight
        case (False, True, False, True):
            return ROOM_TYPES._2s, 0
        case (True, False, True, False):
            return ROOM_TYPES._2s, pi / 2
        # corner
        case z if sum(z) == 2:
            for idx, i in enumerate(z):
                if i and z[idx - 1]:
                    break
            else:
                assert False
            return ROOM_TYPES._2c, (pi / 2 * ((-idx + 0) % 4))

        # 3 exits
        case z if sum(z) == 3:
            for idx, i in enumerate(z):
                if not i:
                    break
            else:
                assert False
            return ROOM_TYPES._3, (pi / 2 * ((-idx + 2) % 4))

        case _:
            assert False, "This one is serious"
