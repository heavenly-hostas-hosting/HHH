import numpy as np
from js import d3, setTimeout, window
from pyodide.ffi import create_proxy

HEIGHT = WIDTH = 500
GRID_SIZE = 100
FPS = 1
GRID_LINES_DISTANCE = WIDTH / GRID_SIZE

GRID = {
    "n": np.zeros((GRID_SIZE,) * 2, dtype=np.uint8),
    "n+1": np.zeros((GRID_SIZE,) * 2, dtype=np.uint8),
}
NEIGHBORS = np.zeros_like(GRID["n"])

svg = (
    d3.select("#my_dataviz")
    .attr("width", WIDTH)
    .attr("height", HEIGHT)
    .append("svg")
    .attr("class", "container-svg")
    .attr("width", WIDTH)
    .attr("height", HEIGHT)
)

svg.append("rect").attr("class", "svg-rect").attr("x", 0).attr("y", 0).attr("height", HEIGHT).attr(
    "width",
    WIDTH,
).style("fill", "EBEBEB")

x = d3.scaleLinear().domain([0, GRID_SIZE]).range([0, WIDTH])

y = d3.scaleLinear().domain([0, GRID_SIZE]).range([HEIGHT, 0])


def init_grid() -> None:
    """Taken function from `experimental/conways_gol.py`."""
    for i in range(-10, 10, 1):
        for j in range(-10, 10, 1):
            GRID["n"][GRID_SIZE // 2 + i, GRID_SIZE // 2 + j] = 1


def update_grid() -> None:
    """Taken function from `experimental/conways_gol.py`."""
    grid_n = GRID["n"]
    grid_nplus1 = GRID["n+1"]
    NEIGHBORS[:-1, :] += grid_n[+1:, :]
    NEIGHBORS[+1:, :] += grid_n[:-1, :]
    NEIGHBORS[:, :-1] += grid_n[:, +1:]
    NEIGHBORS[:, +1:] += grid_n[:, :-1]
    NEIGHBORS[:-1, :-1] += grid_n[+1:, +1:]
    NEIGHBORS[+1:, +1:] += grid_n[:-1, :-1]
    NEIGHBORS[+1:, :-1] += grid_n[:-1, +1:]
    NEIGHBORS[:-1, +1:] += grid_n[+1:, :-1]
    # Any live cell with two or three live (= 2 or 3) neighbours lives on to the next generation.
    # Any dead cell with exactly three live ( = 3) neighbours becomes a live cell, as if by reproduction.
    grid_nplus1 += (NEIGHBORS + grid_n) == 3
    grid_nplus1 += (NEIGHBORS == 3) * grid_n
    # Any live cell with fewer than two live (< 2) neighbours dies as if caused by underpopulation.
    # Any live cell with more than three live (> 3) neighbours dies, as if by overpopulation.
    grid_nplus1 *= 1 - (NEIGHBORS > 3) * grid_n
    grid_nplus1 *= 1 - (NEIGHBORS < 2) * grid_n
    GRID["n"], GRID["n+1"] = grid_nplus1, grid_n
    GRID["n+1"][:, :] = 0
    NEIGHBORS[:, :] = 0


@create_proxy
def next_frame() -> None:
    """Animate to next state."""
    window.requestAnimationFrame(update)


@create_proxy
def update(*_: tuple) -> None:
    """Update the scatterplot at a stable FPS."""
    y_coords, x_coords = GRID["n"].nonzero()
    d3.selectAll(".pixel").remove()
    for x_coord, y_coord in zip(x_coords, y_coords, strict=True):
        svg.append("g").attr("class", "pixel").append("rect").attr("x", x(x_coord)).attr("y", y(y_coord)).attr(
            "width",
            GRID_LINES_DISTANCE,
        ).attr("height", GRID_LINES_DISTANCE).style("fill", "red")
    update_grid()
    setTimeout(next_frame, 1000 / FPS)


init_grid()
update()
