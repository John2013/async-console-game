import asyncio
import time
import curses
from random import randint, choice
from typing import List, Coroutine


def run_coroutines(coroutines: List[Coroutine], canvas, delay=0.):
    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
                canvas.refresh()
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        time.sleep(delay)


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


def draw(canvas):
    row, column = (5, 20)
    curses.curs_set(False)
    canvas.border()
    canvas.addstr(row, column, 'Hello, World!')
    canvas.refresh()
    min_row, min_col = (1, 1)
    max_row, max_col = canvas.getmaxyx()
    max_row -= 2
    max_col -= 2

    symbols = list('+*.:')

    coroutines: List[Coroutine] = []
    stars_count = 135
    for _ in range(stars_count):
        coroutines.append(blink(
            canvas,
            randint(min_row, max_row),
            randint(min_col, max_col),
            choice(symbols)
        ))

    tic_timeout = .1
    run_coroutines(coroutines, canvas, tic_timeout)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
