#!/usr/bin/env python3

""" Countdown numbers game solver  """

import argparse
import copy
import curses
import random
import sys
import time

BOTTOM_NUMS = list(range(1, 11)) * 2
TOP_NUMS = [25, 50, 75, 100]
LINECHARS = ["0", "0", "1", ".", " "]
LINECOLRS = [23, 29, 35]
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


def apply_font(strings, width):
    """Represent a sequence of strings using font

    :param strings [str] : List of strings to print
    :param width int : The screen width

    :returns [str] : List of strings printed using font
    """

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
    """True if b is a factor of a"""
    if b == 0:
        return False
    return (a / b) == (a // b)


def choose_number(numbers):
    """Randomly choose a number from a list and remove it from the list"""

    if numbers:
        num = random.choice(numbers)
        numbers.remove(num)
        return num

    return None


def do_op(a, b, op):
    """Perform an operator on two numbers"""

    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        return a // b

    raise ValueError(f"Unexpected operator {op}")


def remove_unused_steps(steps):
    """Remove any step whose result is not used in subsequent steps

    :param steps [str] : List of solution steps as 'a <op> b = result'
    """

    used_numbers = []
    for step in steps:
        num_a, _op, num_b, _eq, res = step.split()
        used_numbers += [num_a, num_b]
    steps_to_remove = []
    for step in steps[:-1]:
        num_a, _op, num_b, _eq, res = step.split()
        if not res in used_numbers:
            steps_to_remove.append(step)
    for step in steps_to_remove:
        steps.remove(step)


def guess(target, numbers, steps=None, best=None):
    """Guess a solution

    :param target number : the result we want to achieve
    :param numbers [number] : the numbers we can use in the solution
    :param steps list : the steps we have taken so far to reach the
        solution
    :param best tuple : the best solution so far (x, y) where x is the
        amount of error in the solution and y is the steps we took to get
        there

    :returns tuple : the best solution (x, y) where x is the amount of
        error in the solution and y is the steps we took to get there
    """

    numbers = copy.copy(numbers)

    if not steps:
        steps = []

    # if the target is in the list of numbers we have, then we already have the
    # solution
    if target in numbers:
        return 0, [f"{target} = {target}"]

    if not best:
        best = (BIGNUM, ["."])

    # keep trying until we run out of numbers to use
    while numbers:
        num_a = choose_number(numbers)
        num_b = choose_number(numbers)

        if None in (num_a, num_b):
            # we weren't able to get 2 numbers to use in this step, so give up
            break

        if num_b > num_a:
            # num_a should be the higher number, in case we wish to do division
            num_a, num_b = num_b, num_a

        ops = ["+", "-"]

        if 1 not in (num_a, num_b):
            # it's only worth multiplying or dividing if both numbers are not 1
            ops.append("*")
            if is_factor(num_b, num_a):
                # it's only worth dividing if num_b is a factor of num_a
                ops.append("/")

        op = random.choice(ops)

        res = do_op(num_a, num_b, op)

        if res == 0:
            # if performing the op gave a result of 0, that will not be any use
            # in getting closer to the result, so put the numbers back and try
            # again
            numbers += [num_a, num_b]
            continue

        # record the op performed on this step
        opstr = f"{num_a:>4d} {op} {num_b:<4d} = {res:<4d}"

        steps.append(opstr)

        error = abs(res - target)

        if error < best[0]:
            # record this as the best result so far
            best = (error, steps)

        if error == 0:
            # we have reached the target
            break

        # add the result to our group of numbers for potential re-use in
        # subsequent steps
        numbers.append(res)

        # perform another step
        return guess(target, numbers, steps, best)

    return best


def randline(line, width, solution):
    """Randomise a line to generate cool, matrix-y looking rubbish

    :param line tuple : (line text as a string, line color)
    :param width int : Screen width
    :param solution [str] : The game solution thus far

    :returns tuple : (line text as string, line color)
    """

    # our pool of random characters will have some of the solution thus far
    # sprinkled in for variation
    linechars = (LINECHARS * 100) + [y for x in solution for y in x]

    if line is None:
        # a whole line of random junk
        line_txt = "".join([random.choice(linechars) for _ in range(width)])
        line_col = [curses.color_pair(random.choice(LINECOLRS)) for _ in line_txt]
    else:
        # just modify 4 random characters in the line
        for _ in range(random.randint(1, 5)):
            num = random.randint(0, width - 1)
            line_txt = line[0][:num] + random.choice(linechars) + line[0][num + 1 :]
            rcol = curses.color_pair(random.choice(LINECOLRS))
            line_col = line[1][:num] + [rcol] + line[1][num + 1 :]

    return (line_txt, line_col)


def print_all_colors(stdscr):
    """Print all color pairs

    :param stdscr Window : The curses screen object
    """

    for row in range(16):
        for col in range(8):
            color = col + (row * 8)
            ccol = curses.color_pair(color)
            stdscr.addstr(row, col * 5, f"{color:<4} ", ccol)
    stdscr.refresh()
    stdscr.getkey()
    sys.exit()


def has_solution(targ, nums):
    """True if a solution is possible

    :param targ int : The target number
    :param nums [int] : Available numbers to use

    :returns bool : True if a solution is possible
    """

    error, solution = BIGNUM, None

    for _ in range(1000):
        error, solution = guess(targ, nums, best=(error, solution))

    return error == 0


def start_game(stdscr, width, height):
    """Print taget and wait for keypress

    :param stdscr Window : The curses screen object
    :param width int : Screen width
    :param height int : Screen height
    """

    target = [" ".join([str(x) for x in args.nums]), str(args.targ)]
    targ_lines = apply_font(target, width)
    height_mid = (height - (len(target) * 6)) // 2
    for y, s in enumerate(targ_lines):
        ys = height_mid + y
        for x in range(width):
            if x > (len(s) - 1):
                pass
            elif s[x] == " ":
                pass
            else:
                char = s[x]
                color = curses.color_pair(LINECOLRS[-1])
                try:
                    stdscr.addstr(ys, x, char, color)
                except Exception as exp:
                    raise ValueError(f"{ys} {x} {char} {color}") from exp

    stdscr.getkey()


def find_solution(stdscr, width, height):
    """Find the best guess

    :param stdscr Window : The curses screen object
    :param width int : Screen width
    :param height int : Screen height

    :returns tuple : (solution, screen lines, current line number)
    """

    lines = {}
    num_attempts = 0
    error, solution = BIGNUM, None

    # try for a certain amount of time so that is looks like the computer is
    # doing some actual work, even if it finds the answer very quickly
    elapsed = 0
    start = time.time()

    while (error > 0) or elapsed < 4:
        error, solution = guess(args.targ, args.nums, best=(error, solution))

        num_attempts += 1

        # update the screen
        if not num_attempts % 17:
            line_num = num_attempts % height
            lines[line_num] = randline(lines.get(line_num, None), width, solution)

            for x in range(width):
                char = lines[line_num][0][x]
                color = lines[line_num][1][x]
                stdscr.addstr(line_num, x, char, color)

            stdscr.refresh()

        # stop if no solution found
        if num_attempts > 5e5:
            msg = "Couldn't find an exact solution."
            width_mid = (width - len(msg)) // 2
            stdscr.addstr(height // 2, width_mid, msg)
            stdscr.refresh()
            stdscr.getkey()
            break

        elapsed = time.time() - start

    stdscr.refresh()

    return solution, lines, line_num


def print_end(stdscr, width, lines, line_num):
    """Prepare for end of game

    :param stdscr Window : The curses screen object
    :param width int : Screen width
    :param lines dict : Current screen lines
    :param line_num int : Current line number
    """

    target = f"{args.nums} {[args.targ]}"
    color = curses.color_pair(LINECOLRS[-1])
    trgt_start = (width - len(target)) // 2
    trgt_end = trgt_start + len(target)
    stdscr.addstr(1, trgt_start, target, color)
    for x in range(trgt_start, trgt_end):
        color = curses.color_pair(LINECOLRS[-1])
        char = target[x - trgt_start]
        try:
            line = list(lines[1][0])
            line[x] = char
            colors = list(lines[1][1])
            colors[x] = color
            lines[1] = ("".join(line), colors)
            stdscr.addstr(line_num, x, char, color)
        except Exception as exp:
            raise ValueError(f"{lines[1][0][x]}") from exp


def run_game(stdscr):
    """Find solution and print it

    :param stdscr Window : The curses screen object

    :returns bool : True if the game should be exited
    """

    stdscr.clear()
    height, width = stdscr.getmaxyx()
    height -= 1
    width -= 1

    start_game(stdscr, width, height)

    solution, lines, line_num = find_solution(stdscr, width, height)

    print_end(stdscr, width, lines, line_num)

    # print out the best solution
    remove_unused_steps(solution)
    sol_lines = apply_font(solution, width)
    height_mid = (height - (len(solution) * 6)) // 2

    for y, s in enumerate(sol_lines):
        ys = height_mid + y
        for x in range(width):
            if x > (len(s) - 1):
                char = lines[ys][0][x]
                color = lines[ys][1][x]
            elif s[x] == " ":
                char = lines[ys][0][x]
                color = lines[ys][1][x]
            else:
                char = s[x]
                color = curses.color_pair(LINECOLRS[-1])
            stdscr.addstr(ys, x, char, color)

    stdscr.refresh()

    return stdscr.getkey() == "q"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve numbers game.")
    parser.add_argument(
        "-n", "--nums", nargs="+", type=int, help="Numbers", default=None
    )
    parser.add_argument("-t", "--targ", type=int, help="Target", default=None)
    args = parser.parse_args()

    rand_nums = args.nums is None
    rand_targ = args.targ is None
    randomized = rand_nums or rand_targ

    def random_problem():
        """Generate a random promblem to solve"""

        while True:
            nums, targ = args.nums, args.targ
            if rand_nums:
                n_top = random.randint(0, len(TOP_NUMS) + 1)
                random.shuffle(TOP_NUMS)
                random.shuffle(BOTTOM_NUMS)
                nums = TOP_NUMS[:n_top] + BOTTOM_NUMS[: 6 - n_top]
            if rand_targ:
                targ = random.randint(101, 1000)
            if has_solution(targ, nums):
                args.nums, args.targ = nums, targ
                break

    curses.initscr()
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for i in range(curses.COLORS):
        curses.init_pair(i, i, -1)
    if not randomized:
        curses.wrapper(run_game)
    else:
        while True:
            random_problem()
            if curses.wrapper(run_game):
                break
