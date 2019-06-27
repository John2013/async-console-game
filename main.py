import asyncio
import time
import curses
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
    row, column = (3, 7)
    margin = 1
    coroutines: List[Coroutine] = []
    for star_number in range(5):
        current_column = column + star_number + margin * star_number
        coroutines.append(blink(canvas, row, current_column))

    tic_timeout = .1
    run_coroutines(coroutines, canvas, tic_timeout)
    # while True:
    #     canvas.refresh()
    #     row, column = (3, 7)
    #     canvas.addstr(row, column, '*', curses.A_DIM)
    #     canvas.refresh()
    #     time.sleep(2.)
    #     canvas.addstr(row, column, '*', curses.A_NORMAL)
    #     canvas.refresh()
    #     time.sleep(.3)
    #     canvas.addstr(row, column, '*', curses.A_BOLD)
    #     canvas.refresh()
    #     time.sleep(.5)
    #     canvas.addstr(row, column, '*', curses.A_NORMAL)
    #     canvas.refresh()
    #     time.sleep(.3)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
