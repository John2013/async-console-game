import asyncio
import time
import curses


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


def draw(canvas):
    row, column = (5, 20)
    curses.curs_set(False)
    canvas.border()
    canvas.addstr(row, column, 'Hello, World!')
    canvas.refresh()
    row, column = (3, 7)
    corutine = blink(canvas, row, column)
    corutine.send(None)
    canvas.refresh()
    time.sleep(12)
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
    time.sleep(12)
