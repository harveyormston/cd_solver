""" countdown numbers game solver  """

import copy
import random
import sys
import argparse
import curses

LINECHARS = ['0', '0', '1', '.', ' ']
LINECOLRS = [23, 29, 35, 41]
BIGNUM = 1e32

FONT = {
    "0": ["█████",
          "██ ██",
          "██ ██",
          "██ ██",
          "█████"],

    "1": [" ███ ",
          "████ ",
          " ███ ",
          " ███ ",
          "█████"],

    "2": ["█████",
          "   ██",
          "█████",
          "██   ",
          "█████"],

    "3": ["█████",
          "   ██",
          " ████",
          "   ██",
          "█████"],

    "4": ["██ ██",
          "██ ██",
          "█████",
          "   ██",
          "   ██"],

    "5": ["█████",
          "██   ",
          "█████",
          "   ██",
          "█████"],

    "6": ["█████",
          "██   ",
          "█████",
          "██ ██",
          "█████"],

    "7": ["█████",
          "   ██",
          "   ██",
          "   ██",
          "   ██"],

    "8": ["█████",
          "██ ██",
          "█████",
          "██ ██",
          "█████"],

    "9": ["█████",
          "██ ██",
          "█████",
          "   ██",
          "█████"],

    "+": ["     ",
          "  █  ",
          "█████",
          "  █  ",
          "     "],

    "-": ["     ",
          "     ",
          "█████",
          "     ",
          "     "],

    "/": ["  █  ",
          "     ",
          "█████",
          "     ",
          "  █  "],

    "*": ["     ",
          " █ █ ",
          "  █  ",
          " █ █ ",
          "     "],

    "=": ["     ",
          "█████",
          "     ",
          "█████",
          "     "],

    " ": ["     ",
          "     ",
          "     ",
          "     ",
          "     "],
}


def print_font(strings, width):
    """ print a set of strings using font """

    lines = []
    for s in strings:
        for row in range(5):
            line = []
            for c in s:
                line.append(" " + FONT[c][row])
            line = "".join(line)
            if len(line) < width:
                front_pad = (width - len(line)) // 2
                back_pad = len(line) + front_pad - width
                line = (" " * front_pad) + line + (" " * back_pad)
            lines.append(line)
        lines.append("")
    return lines


def is_factor(b, a):
    """ True is b is a factor of a """
    if b == 0:
        return False
    return (a / b) == (a // b)


def choose_number(numbers):
    """ Randomly a number """

    if numbers:
        num = random.choice(numbers)
        numbers.remove(num)
        return num

    return None


def do_op(a, b, op):
    """ Perform an operator on two numbers """

    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    if op == '/':
        return a // b

    return None


def guess(target, numbers, steps=None, best=None):
    """ Guess a solution  """

    numbers = copy.copy(numbers)

    if not steps:
        steps = []

    if target in numbers:
        return 0, ["{0} = {0}".format(target)]

    if not best:
        best = [BIGNUM, '.']

    while numbers:

        num_a = choose_number(numbers)
        num_b = choose_number(numbers)

        if None in (num_a, num_b):
            break

        if num_b > num_a:
            num_a, num_b = num_b, num_a

        if is_factor(num_b, num_a):
            op = random.choice(['+', '-', '*', '/'])
        else:
            op = random.choice(['+', '-', '*'])

        res = do_op(num_a, num_b, op)

        if res == 0:
            continue

        opstr = "{:>4d} {} {:<4d} = {:<4d}".format(num_a, op, num_b, res)

        steps.append(opstr)

        error = abs(res - target)

        if error < best[0]:
            best[0] = error
            best[1] = steps
            break

        if error == 0:
            break

        numbers.append(res)

        return guess(target, numbers, steps, best)

    return best


def randline(line, num, width, solution):
    """ randomised line of cool, matrix-y looking rubbish """

    linechars = LINECHARS * 100

    solution_chars = [y for x in solution for y in x]
    linechars += solution_chars

    if line is None:
        return ''.join([random.choice(linechars) for _ in range(width)])

    num = random.randint(0, width - 1)
    line = line[:num] + random.choice(linechars) + line[num + 1:]

    return line


def main(stdscr):
    """ main function """

    num_attempts = 0
    error, solution = BIGNUM, None

    stdscr.clear()
    height, width = stdscr.getmaxyx()
    height -= 1
    width -= 1
    lines = {}

    # find the best guess
    while (error > 0) or num_attempts < 1e4:

        error, solution = guess(args.targ, args.nums, best=[error, solution])

        num_attempts += 1

        # update the screen
        if not num_attempts % 101:

            line_num = num_attempts % height
            line = lines.get(line_num, None)
            lines[line_num] = randline(line, line_num, width, solution)

            for x in range(width):

                color = curses.color_pair(random.choice(LINECOLRS))
                char = lines[line_num][x]
                stdscr.addstr(line_num, x, char, color)

            stdscr.refresh()

        # stop if no solution found
        if num_attempts > 1e6:

            msg = "Couldn't find an exact solution."
            width_mid = (width - len(msg)) // 2
            stdscr.addstr(height // 2, width_mid, msg)
            stdscr.refresh()
            stdscr.getkey()
            break

    stdscr.refresh()

    # print out the best solution
    height_mid = (height - len(solution)) // 2
    width_mid = (width - max([len(x) for x in solution])) // 2

    target = "{} {}".format(args.nums, [args.targ])
    stdscr.addstr(height_mid - 2, (width - len(target)) // 2, target)

    sol_lines = print_font(solution, width)

    height_mid = (height - (len(solution) * 5)) // 2
    for y, s in enumerate(sol_lines):
        ys = height_mid + y
        for x in range(width):
            color = curses.color_pair(random.choice(LINECOLRS))
            if x > (len(s) - 1):
                char = lines[ys][x]
            elif s[x] == " ":
                char = lines[ys][x]
            else:
                char = s[x]
                color = curses.COLOR_WHITE
            stdscr.addstr(ys, x, char, color)

    stdscr.refresh()
    stdscr.getkey()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Solve numbers game.')
    parser.add_argument('-n', '--nums', nargs='+', type=int, help='<Required> Numbers', required=True)
    parser.add_argument('-t', '--targ', type=int, help='<Required> Target', required=True)
    args = parser.parse_args()

    curses.initscr()
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for i in range(curses.COLORS):
        curses.init_pair(i, i, -1)
    curses.wrapper(main)
