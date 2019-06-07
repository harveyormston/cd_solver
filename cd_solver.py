""" countdown numbers game solver  """

import copy
import random
import sys
import argparse
import curses

LINECHARS = ['0', '0', '1', '.', ' ']
LINECOLRS = [23, 29, 35, 41]


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


def guess(target, numbers, steps=None):
    """ Guess a solution  """

    numbers = copy.copy(numbers)

    if not steps:
        steps = []

    if target in numbers:
        return ["{0} = {0}".format(target)]

    while numbers:

        num_a = choose_number(numbers)
        num_b = choose_number(numbers)

        if None in (num_a, num_b):
            return False

        if num_b > num_a:
            num_a, num_b = num_b, num_a

        if is_factor(num_b, num_a):
            op = random.choice(['+', '-', '*', '/'])
        else:
            op = random.choice(['+', '-', '*'])

        res = do_op(num_a, num_b, op)

        opstr = "{:>4d} {} {:<4d} = {}".format(num_a, op, num_b, res)

        steps.append(opstr)

        if res == target:
            return steps

        numbers.append(res)
        return guess(target, numbers, steps)

    return False


def randline(line, num, width):
    """ randomised line of cool, matrix-y looking rubbish """

    linechars = LINECHARS + [' ' for _ in range(num // 10)]

    if line is None:
        return ''.join([random.choice(linechars) for _ in range(width)])

    num = random.randint(0, width - 1)
    line = line[:num] + random.choice(linechars) + line[num + 1:]

    return line


def main(stdscr):
    """ main function """

    num_attempts = 0
    solution = None

    stdscr.clear()
    height, width = stdscr.getmaxyx()
    height -= 1
    width -= 1
    lines = {}

    while (not solution) or num_attempts < 1e4:

        solution = guess(args.targ, args.nums)
        num_attempts += 1

        if not (num_attempts % 111):
            line_num = num_attempts % height
            line = lines.get(line_num, None)
            lines[line_num] = randline(line, line_num, width)
            for x in range(width):
                color = curses.color_pair(random.choice(LINECOLRS))
                char = lines[line_num][x]
                stdscr.addstr(line_num, x, char, color)
            stdscr.refresh()

        if num_attempts > 1e6:
            msg = "Couldn't find a solution."
            width_mid = (width - len(msg)) // 2
            stdscr.addstr(height // 2, width_mid, msg)
            stdscr.refresh()
            stdscr.getkey()
            sys.exit(1)

    for y in range(height):
        stdscr.addstr(y, 0, ' ' * width)
    stdscr.refresh()

    height_mid = (height - len(solution)) // 2
    width_mid = (width - max([len(x) for x in solution])) // 2
    for y, s in enumerate(solution):
        stdscr.addstr(height_mid + y, width_mid, s)
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
