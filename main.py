import asyncio
import os
import time
import curses
from random import randint, choice
from typing import List, Coroutine

from curses_tools import draw_frame, read_controls, get_frame_size

coroutines: List[Coroutine] = []


def run_coroutines(coroutines: List[Coroutine], canvas, tic_timeout=0.):
    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()
        time.sleep(tic_timeout)


def get_playground_border(canvas):
    min_row, min_col = (1, 1)
    max_row, max_col = canvas.getmaxyx()
    canvas_padding = 2
    max_row -= canvas_padding
    max_col -= canvas_padding
    return min_row, min_col, max_row, max_col


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

    min_row, min_col, max_row, max_col = get_playground_border(canvas)

    curses.beep()

    while min_row < row < max_row and min_col < column < max_col:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def ship(canvas, row, column, frames):
    min_row, min_col, max_row, max_col = get_playground_border(canvas)
    while True:
        for frame in frames:
            rows_direction, columns_direction, space_pressed = read_controls(canvas)
            row += rows_direction
            column += columns_direction

            if row < min_row:
                row += 1
            if column < min_col:
                column += 1

            rows, cols = get_frame_size(frame)

            if row + rows > max_row:
                row -= 1

            if column + cols > max_col:
                column -= 1

            draw_frame(canvas, row, column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, frame, negative=True)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """
    Animate garbage, flying from top to bottom.
    Column position will stay same, as specified on start.
    """
    min_row, min_col, max_row, max_col = get_playground_border(canvas)

    column = max(column, min_col)
    column = min(column, max_col)

    row = min_row

    while row < max_row:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


async def fill_orbit_with_garbage(canvas, tens_milliseconds_timeout: int=5):
    garbage_frames = get_frames('./garbage')

    min_row, min_col, max_row, max_col = get_playground_border(canvas)

    while True:
        column = randint(min_col, max_col)
        frame = choice(garbage_frames)

        coroutines.append(fly_garbage(canvas, column, frame))
        for _ in range(tens_milliseconds_timeout):
            await asyncio.sleep(0)


def get_frames(path):
    frames = []
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        with open(filepath, 'r') as file:
            frames.append(file.read())
    return frames


def get_random_coords(min_row, max_row, min_col, max_col):
    return (
        randint(min_row, max_row),
        randint(min_col, max_col),
    )


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)
    canvas.refresh()

    min_row, min_col, max_row, max_col = get_playground_border(canvas)

    symbols = list('+*.:')

    stars_coords = []
    stars_count = 200

    for _ in range(stars_count):
        start_step = randint(1, 4)
        new_coords = get_random_coords(min_row, max_row, min_col, max_col)
        while new_coords in stars_coords:
            new_coords = get_random_coords(min_row, max_row, min_col, max_col)

        coroutines.append(blink(
            canvas,
            *new_coords,
            choice(symbols),
            start_step
        ))
        stars_coords.append(new_coords)

    del stars_coords

    center_row = int(round((max_row - min_row) / 2))
    center_col = int(round((max_col - min_col) / 2))

    coroutines.append(
        fire(canvas, center_row, center_col)
    )

    ship_frames = get_frames('./ship')
    coroutines.append(
        ship(canvas, center_row - 1, center_col - 2, ship_frames)
    )

    coroutines.append(fill_orbit_with_garbage(canvas))

    tic_timeout = .1
    run_coroutines(coroutines, canvas, tic_timeout)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
