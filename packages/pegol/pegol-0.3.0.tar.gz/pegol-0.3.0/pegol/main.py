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
    stdscr.timeout(100)

    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)

    hearts = ["♥", "♡", "♣", "♦", "♠"]
    max_y, max_x = stdscr.getmaxyx()
    drops = [[random.randint(1, max_x-2), random.randint(1, max_y-2)] for _ in range(100)]

    message = "The World's Most Powerful Congratulation!"
    sub_message = "Wish you endless joy and love ♥"
    name = "From Pegol"

    while True:
        stdscr.clear()
        try:
            stdscr.addstr(max_y//2 - 4, (max_x - len(message))//2, message, curses.A_BOLD)
            stdscr.addstr(max_y//2 - 2, (max_x - len(sub_message))//2, sub_message, curses.color_pair(1))
            stdscr.addstr(max_y//2, (max_x - len(name))//2, name, curses.A_ITALIC)
        except:
            pass

        for i, (x, y) in enumerate(drops):
            if 0 < x < max_x-1 and 0 < y < max_y-1:
                try:
                    stdscr.addstr(y, x, random.choice(hearts), curses.color_pair(random.randint(1,3)))
                except:
                    pass
            drops[i][1] += 1
            if drops[i][1] >= max_y-1:
                drops[i] = [random.randint(1, max_x-2), 0]

        stdscr.refresh()
        time.sleep(0.1)

        if stdscr.getch() != -1:
            break

def main():
    print("Hello, thanks for installing pegol! It was made by Pegol Reda Shokry.")
    user_input = input('Type "pegolpro" for fun: ')
    if user_input.strip().lower() == "pegolpro":
        print("🎉 You typed pegolpro! Fun activated!")
        if curses:
            try:
                curses.wrapper(draw_hearts)
            except Exception as e:
                print(f"Error occurred: {str(e)}")
        else:
            print("Curses not available on this system. Try installing windows-curses on Windows.")
        print("\nThanks for watching! ♥")
    else:
        print("You didn't type pegolpro. Try again next time!")
