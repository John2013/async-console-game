import asyncio
import os
import time
import curses
from random import randint, choice
from typing import List, Coroutine

from curses_tools import draw_frame, read_controls, get_frame_size
from explosion import explode
from obstacles import Obstacle
from physics import update_speed

coroutines: List[Coroutine] = []
spaceship_frame_number = 0
obstacles: List[Obstacle] = []
obstacles_in_last_collision: List[Obstacle] = []


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


def get_playground_limits(canvas):
    min_row, min_col = (1, 1)
    max_row, max_col = canvas.getmaxyx()
    canvas_padding = 2
    max_row -= canvas_padding
    max_col -= canvas_padding
    return min_row, min_col, max_row, max_col


def show_game_over(canvas):
    frame = get_frames('./gameover')[0]
    rows, cols = get_frame_size(frame)

    min_row, min_col, max_row, max_col = get_playground_limits(canvas)

    width = max_col - min_col
    height = max_row - min_row

    frame_row = round((height - rows) / 2) + min_row
    frame_col = round((width - cols) / 2) + min_col

    draw_frame(canvas, frame_row, frame_col, frame)


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*', start_step=0):
    while True:
        if start_step <= 1:
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await sleep(20)

        if start_step <= 2:
            canvas.addstr(row, column, symbol)
            await sleep(3)

        if start_step <= 3:
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)
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

    min_row, min_col, max_row, max_col = get_playground_limits(canvas)

    curses.beep()

    while min_row < row < max_row and min_col < column < max_col:
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collision.append(obstacle)
                return

        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def run_spaceship(canvas, row, column, frames):
    min_row, min_col, max_row, max_col = get_playground_limits(canvas)
    row_speed = column_speed = 0
    shoot_top = -1
    shoot_left = 2
    shoot_base_row_speed = - .3
    while True:
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction,
                                               columns_direction)
        row += row_speed
        column += column_speed

        if row < min_row:
            row += 1
        if column < min_col:
            column += 1

        rows, cols = get_frame_size(frames[spaceship_frame_number])

        if row + rows > max_row:
            row -= 1

        if column + cols > max_col:
            column -= 1

        if space_pressed:
            shoot_row_speed = shoot_base_row_speed
            if row_speed < 0:
                shoot_row_speed += row_speed
            coroutines.append(
                fire(
                    canvas,
                    row + shoot_top,
                    column + shoot_left,
                    shoot_row_speed
                )
            )
        for obstacle in obstacles:
            if obstacle.has_collision(row, column, rows, cols):
                show_game_over(canvas)
                return

        frame = frames[spaceship_frame_number]
        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)


async def animate_spaceship(frames):
    global spaceship_frame_number
    while True:
        spaceship_frame_number = (spaceship_frame_number + 1) % len(frames)
        await sleep(2)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """
    Animate garbage, flying from top to bottom.
    Column position will stay same, as specified on start.
    """
    min_row, min_col, max_row, max_col = get_playground_limits(canvas)

    column = max(column, min_col)
    column = min(column, max_col)

    row = min_row

    rows, cols = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, rows, cols)
    obstacles.append(obstacle)
    center_row = round(rows / 2)
    center_col = round(cols / 2)

    while row < max_row:
        if row > max_row:
            obstacles.remove(obstacle)
        if obstacle in obstacles_in_last_collision:
            obstacles.remove(obstacle)
            obstacles_in_last_collision.remove(obstacle)
            del obstacle
            await explode(canvas, row + center_row, column + center_col)
            return
        obstacle.row = row
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


async def fill_orbit_with_garbage(canvas, tics_timeout: int = 5):
    garbage_frames = get_frames('./garbage')

    min_row, min_col, max_row, max_col = get_playground_limits(canvas)

    while True:
        column = randint(min_col, max_col)
        frame = choice(garbage_frames)

        coroutines.append(fly_garbage(canvas, column, frame))
        await sleep(tics_timeout)


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

    min_row, min_col, max_row, max_col = get_playground_limits(canvas)

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

    ship_frames = get_frames('./ship')
    coroutines.append(
        run_spaceship(canvas, center_row - 1, center_col - 2, ship_frames)
    )
    coroutines.append(
        animate_spaceship(ship_frames)
    )

    coroutines.append(fill_orbit_with_garbage(canvas))

    tic_timeout = .1
    run_coroutines(coroutines, canvas, tic_timeout)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
