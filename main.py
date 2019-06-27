import asyncio
import os
import time
import curses
from random import randint, choice
from typing import List, Coroutine

from curses_tools import draw_frame


def run_coroutines(coroutines: List[Coroutine], tic_timeout=0.):
    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        time.sleep(tic_timeout)


async def blink(canvas, row, column, symbol='*', start_step=0):
    while True:
        if start_step <= 1:
            canvas.addstr(row, column, symbol, curses.A_DIM)
            for _ in range(20):
                await asyncio.sleep(0)

        if start_step <= 2:
            canvas.addstr(row, column, symbol)
            for _ in range(3):
                await asyncio.sleep(0)

        if start_step <= 3:
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            for _ in range(5):
                await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)
        start_step = 0


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 2, columns - 2
    min_row, min_col = 1, 1

    curses.beep()

    while min_row < row < max_row and min_col < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def ship(canvas, row, column, frames):
    while True:
        for frame in frames:
            draw_frame(canvas, row, column, frame)
            canvas.refresh()
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, frame, negative=True)


def get_frames(path):
    frames = []
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        with open(filepath, 'r') as file:
            frames.append(file.read())
    return frames


def draw(canvas):
    row, column = (5, 20)
    curses.curs_set(False)
    canvas.border()
    canvas.addstr(row, column, 'Hello, World!')
    canvas.refresh()
    min_row, min_col = (1, 1)
    max_row, max_col = canvas.getmaxyx()
    canvas_padding = 2
    max_row -= canvas_padding
    max_col -= canvas_padding

    symbols = list('+*.:')

    coroutines: List[Coroutine] = []
    stars_count = 150
    for _ in range(stars_count):
        start_step = randint(1, 4)
        coroutines.append(blink(
            canvas,
            randint(min_row, max_row),
            randint(min_col, max_col),
            choice(symbols),
            start_step
        ))

    center_row = int(round((max_row - min_row) / 2))
    center_col = int(round((max_col - min_col) / 2))

    coroutines.append(
        fire(canvas, center_row, center_col)
    )

    ship_frames = get_frames('./ship')
    coroutines.append(
        ship(canvas, center_row - 1, center_col - 2, ship_frames)
    )

    tic_timeout = .1
    run_coroutines(coroutines, tic_timeout)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
