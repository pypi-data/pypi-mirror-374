"""Pegol package v3"""
__version__ = "0.3.0"

import time
import random
import sys

# Import curses (windows-curses must be installed on Windows)
try:
    import curses
except ImportError:
    curses = None


def draw_hearts(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(80)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_MAGENTA, -1)
    curses.init_pair(3, curses.COLOR_CYAN, -1)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)
    curses.init_pair(5, curses.COLOR_GREEN, -1)

    hearts = ["♥", "♡", "❤", "❥", "💕", "💖", "💞"]
    max_y, max_x = stdscr.getmaxyx()
    drops = [[random.randint(1, max_x-2), random.randint(1, max_y-2)] for _ in range(120)]

    message = "The World's Most Powerful Congratulation!"
    sub_message = "Wish you endless joy and love ♥"
    mom_message = "Love you, Mom ♥"
    name = "From Pegol"

    color_cycle = [1, 2, 3, 4, 5]
    color_index = 0

    while True:
        stdscr.clear()
        try:
            stdscr.addstr(max_y//2 - 5, (max_x - len(message))//2, message, curses.A_BOLD | curses.color_pair(color_cycle[color_index]))
            stdscr.addstr(max_y//2 - 3, (max_x - len(sub_message))//2, sub_message, curses.color_pair(1))
            stdscr.addstr(max_y//2 - 1, (max_x - len(mom_message))//2, mom_message, curses.color_pair(4) | curses.A_BOLD)
            stdscr.addstr(max_y//2 + 1, (max_x - len(name))//2, name, curses.A_ITALIC | curses.color_pair(2))
        except:
            pass

        for i, (x, y) in enumerate(drops):
            if 0 < x < max_x-1 and 0 < y < max_y-1:
                try:
                    stdscr.addstr(y, x, random.choice(hearts), curses.color_pair(random.choice(color_cycle)))
                except:
                    pass
            drops[i][1] += 1
            if drops[i][1] >= max_y-1:
                drops[i] = [random.randint(1, max_x-2), 0]

        stdscr.refresh()
        time.sleep(0.08)

        color_index = (color_index + 1) % len(color_cycle)

        if stdscr.getch() != -1:
            break


def main():
    if curses:
        try:
            curses.wrapper(draw_hearts)
        except Exception as e:
            print(f"Error occurred: {str(e)}")
    else:
        print("Curses not available on this system. Try installing windows-curses on Windows.")
