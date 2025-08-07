# Conway's Game of Life in python with a live animated matplotlib display
# Works on Pyodide!!
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

GRID_SIZE = 100
GRID = {
    "n": np.zeros((GRID_SIZE,) * 2, dtype=np.uint8),
    "n+1": np.zeros((GRID_SIZE,) * 2, dtype=np.uint8),
}
NEIGHBORS = np.zeros_like(GRID["n"])

fig, ax = plt.subplots()


def init_grid() -> None:
    for i in range(-10, 10, 1):
        for j in range(-10, 10, 1):
            GRID["n"][GRID_SIZE // 2 + i, GRID_SIZE // 2 + j] = 1


def update_grid():
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


def init():
    init_grid()
    ax.set_xlim(0, GRID_SIZE)
    ax.set_ylim(0, GRID_SIZE)
    y, x = GRID["n"].nonzero()
    sc = ax.scatter(x, y)
    return (sc,)


def update(*_):
    update_grid()
    y, x = GRID["n"].nonzero()
    if x.shape[0] == 0:
        init_grid()
    ax.clear()
    ax.set_xlim(0, GRID_SIZE)
    ax.set_ylim(0, GRID_SIZE)
    sc = ax.scatter(x, y)
    return (sc,)


ani = animation.FuncAnimation(fig, update, init_func=init, interval=100, blit=True)
plt.show()
