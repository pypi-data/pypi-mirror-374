# Copyright (C) 2025, Florent Gallaire <fgallaire@gmail.com>
#
# pylint: disable=exec-used, protected-access

"""Module providing the Execubot class and its convenient functions."""

import os
import sys
import time

# A grid can have the standard format or the short format
Grid = list[list[str]] | list[str]


def timer(f):
    """Brython friendly decorator to handle timeout."""
    def wrapper(self, *args):
        if time.time() - self.start > self.timeout:
            raise TimeoutError
        return f(self, *args)
    return wrapper


class Execubot:
    """Execubot level solver."""
    colors = {'p': "purple", 'y': "yellow", 'g': "green", 'b': "blue", 'r': "red",
              'o': "orange", 'm': "maroon", 'w': "white", 'f': "fuchsia"}
    directions = {"left": (-1, 0), "right": (1, 0), "up": (0, -1), "down": (0, 1)}
    timeout = 1

    def __init__(self, code: str, grid: Grid, row: int, col: int):
        self.code = code
        self.grid = self.stdgrid(grid)
        self.row = row
        self.col = col
        self.coord = (col, row)
        self.size = (len(self.grid[0]), len(self.grid))
        self.solution = []
        self.start = 0.0

    @classmethod
    def stdgrid(cls, grid: Grid) -> list[list[str]]:
        """Return a standard format grid."""
        if isinstance(grid[0], str):
            return [['-'.join([cls.colors[clr] for clr in clrs]) for clrs in line.split()] for line in grid]
        return grid

    @staticmethod
    def lindex() -> int:
        """Return the line index in the source code."""
        return sys._getframe(4).f_lineno - 1

    @timer
    def color(self, color: str) -> bool:
        """Test if the cell color is color."""
        x, y = self.coord
        return color in self.grid[y][x]

    @timer
    def direction(self, direction: str):
        """Add direction to the solution."""
        self.solution.append((direction.capitalize(), self.lindex()))
        dx, dy = self.directions[direction]
        x, y = self.coord
        w, h = self.size
        self.coord = ((x + dx) % w, (y + dy) % h)

    def solver(self) -> list[tuple[str, int]]:
        """Return the level solution."""
        colorsd = {color: lambda c=color: self.color(c) for color in self.colors.values()}
        directionsd = {direction: lambda d=direction: self.direction(d) for direction in self.directions}
        self.start = time.time()
        exec(self.code, colorsd | directionsd)
        return self.solution

    @classmethod
    def extractor(cls, level: str, legacy: bool) -> dict[str, Grid | str | int]:
        """Python level extractor."""
        if os.path.isfile(level) and os.path.splitext(level)[1] == '.py':
            with open(level, encoding="utf-8") as f:
                code_py = f.readlines()
        else:
            code_py = level.splitlines(keepends=True)
        lcode = len(code_py)
        i = 0
        while i < lcode and code_py[i].strip():
            i = i + 1
        if i == lcode:
            raise ExecubotLevelFormatError("A blank line between the header and the Python code is required.")
        d = {}
        level_id = os.path.splitext(os.path.basename(level))[0][5:]
        if level_id.isdigit():
            d["level_id"] = int(level_id)
        d["code"] = ''.join(code_py[i+1:])
        exec(''.join(code_py[:i]), {}, d)
        if "grid" not in d:
            raise ExecubotLevelFormatError("A grid variable is required.")
        if legacy:
            d = {k: v for k, v in d.items() if k in cls.__init__.__code__.co_varnames}
        return d


class ExecubotLevelFormatError(Exception):
    """Custom Execubot exception."""


def stdgrid(grid: Grid) -> list[list[str]]:
    """Convenient interface to the stdgrid @classmethod."""
    return Execubot.stdgrid(grid)


def extractor(level: str, legacy: bool = False) -> dict[str, Grid | str | int]:
    """Convenient interface to the extractor @classmethod."""
    return Execubot.extractor(level, legacy)


def solver(code: str, grid: Grid, row: int = 0, col: int = 0) -> list[tuple[str, int]]:
    """Convenient interface to the solver method."""
    return Execubot(code, grid, row, col).solver()


def solve(level: str) -> list[tuple[str, int]]:
    """Convenient solve function."""
    return solver(**extractor(level, True))
