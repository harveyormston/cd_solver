""" countdown numbers game solver  """

import copy
import random
import sys
import argparse

# LINECHARS = ['0', '1', '.', '*', '$', '/', '|', '#']
LINECHARS = ['0', '0', '1', ' ']


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


def do_op(a, b, op):
    """ Perform an operator on two numbers """

    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    elif op == '/':
        return a // b


def guess(target, numbers, steps=None):

    numbers = copy.copy(numbers)

    if not steps:
        steps = []

    if target in numbers:
        return ["{} = {}".format(target, target)]

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

        else:
            numbers.append(res)
            return guess(target, numbers, steps)

    return False


def randline(line):

    if line is None:
        line = random.choice(LINECHARS)
    elif len(line) > 2:
        idx = random.randint(1, len(line) - 1)
        line = line[:idx] + random.choice(LINECHARS) + line[idx + 1:]

    for ch in line:
        sys.stdout.write('\x1b[{};32;40m'.format(random.randint(0, 2)))
        sys.stdout.write(ch)
    sys.stdout.write('\x1b[0m')

    sys.stdout.flush()
    sys.stdout.write('\b' * len(line))

    if len(line) < 80 and random.choice([True, False, False, False]):
        line = line + random.choice(LINECHARS)

    return line


def main():

    parser = argparse.ArgumentParser(description='Solve numbers game.')
    parser.add_argument('-n','--nums', nargs='+', type=int, help='<Required> Numbers', required=True)
    parser.add_argument('-t','--targ', type=int, help='<Required> Target', required=True)
    args = parser.parse_args()

    num_attempts = 0
    solution = None
    line = None

    while not solution:

        solution = guess(args.targ, args.nums)
        num_attempts += 1

        if num_attempts % 10 == 0:
            line = randline(line)
        if num_attempts % 500 == 0 and len(line) == 80:
            line = None
            print()

        if num_attempts > 1e6:
            print("\nCouldn't find a solution.")
            sys.exit(1)

    print("\n\n" + "\n".join(solution))


if __name__ == '__main__':
    main()
