import time
import curses


def draw(canvas):
    row, column = (5, 20)
    curses.curs_set(False)
    canvas.border()
    canvas.addstr(row, column, 'Hello, World!')
    canvas.refresh()
    while True:
        row, column = (3, 7)
        canvas.addstr(row, column, '*', curses.A_DIM)
        canvas.refresh()
        time.sleep(2.)
        canvas.addstr(row, column, '*', curses.A_NORMAL)
        canvas.refresh()
        time.sleep(.3)
        canvas.addstr(row, column, '*', curses.A_BOLD)
        canvas.refresh()
        time.sleep(.5)
        canvas.addstr(row, column, '*', curses.A_NORMAL)
        canvas.refresh()
        time.sleep(.3)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
