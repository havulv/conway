#!/usr/bin/env python3

''' Conway's Game of Life '''

import argparse
import random
import time
import sys
import os


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def check_close(living, i, j):
    ''' Logic for adding up the neighbors of a particular cell '''

    neighbors = 0
    col_len = len(living) - 1
    row_len = len(living[i]) - 1

    # Middle Pieces
    if 0 < i < col_len and 0 < j < row_len:
        for k in range(-1, 2):
            neighbors += sum(living[i+k][j-1:j+2])
        neighbors -= living[i][j]

    # Top Piece
    elif i == 0 and 0 < j < row_len:
        for k in range(0,2):
            neighbors += sum(living[i+k][j-1:j+2])
        neighbors += sum(living[-1][j-1:j+2])
        neighbors -= living[i][j]

    # Bottom Piece
    elif i == col_len and 0 < j < row_len:
        for k in range(-1,1):
            neighbors += sum(living[i+k][j-1:j+2])
        neighbors += sum(living[0][j-1:j+2])
        neighbors -= living[i][j]

    # Left Side
    elif 0 < i < col_len and j == 0:
        for k in range(-1,2):
            neighbors += sum(living[i+k][j:j+2])
            neighbors += living[i+k][-1]
        neighbors -= living[i][j]

    # Right Side
    elif 0 < i < col_len and j == row_len:
        for k in range(-1,2):
            neighbors += sum(living[i+k][j-1:j+1])
            neighbors += living[i+k][0]
        neighbors -= living[i][j]

    # Top Left Corner
    elif i == 0 and j == 0:
        neighbors += living[i][j+1] + living[i+1][j+1] + living[i+1][j]
        neighbors += living[i][-1] + living[-1][-1] + living[-1][j]

    # Top Right Corner
    elif i == 0 and j == row_len:
        neighbors += living[i][j-1] + living[i+1][j-1] + living[i+1][j]
        neighbors += living[i][0] + living[-1][-1] + living[-1][j]

    # Bottom Right Corner
    elif i == col_len and j == row_len:
        neighbors += living[i][j-1] + living[i-1][j-1] + living[i-1][j]
        neighbors += living[0][0] + living[-1][0] + living[0][-1]

    # Bottom Left Corner
    elif i ==col_len and j == 0:
        neighbors += living[i][j+1] + living[i-1][j+1] + living[i-1][j]
        neighbors += living[0][j] + living[-1][-1] + living[0][-1]

    return neighbors


def proliferate(current):
    ''' Compute the death and life of my little cell minions!!!'''

    # Make a deep copy to return afterwards (Can't change while iterating)
    gen_after = [[False for i in j] for j in current]
    deaths = 0

    for ind, row in enumerate(current):
        for jind, col in enumerate(row):
            neighbors = check_close(current, ind, jind)

            if (col and neighbors < 2) or (col and neighbors > 3):
                gen_after[ind][jind] = False
            if (neighbors == 3 or neighbors == 2) and col:
                gen_after[ind][jind] = True
            if not col and neighbors == 3:
                gen_after[ind][jind] = True

        deaths += sum(gen_after[ind])

    return gen_after, deaths


def store(current, count):
    ''' Keep the generationerations instead of throwing them out '''
    end = 0
    generations = []
    while end < count:
        generations.append(current)
        gen_after, Death = proliferate(current)
        there, generation = repetition_look(generations)
        if there or not Death:
            end = count
    return generation


def repetition_look(generations):
    ''' Check if the generation was there previously '''
    if generations[-1] in generations[:-1]:
        return True, generations[-1]
    else:
        return False, []


def print_generation(generation):
    ''' Print generation to screen '''
    for row in generation:
        print("".join(["& " if col else "  " for col in row]))


def potential_seed(size=30, u_bound=0.2, tries=40, time=50):
    good_seeds = []
    for i in range(tries):
        generation = generation_rand_seed(size, u_bound)
        potent_seed = store(generation)
        if potent_seed:
            good_seeds.append(potent_seed)
    return good_seeds


def generation_rand_seed(size, u_bound):
    ''' generationerate a randome seed for the Game '''
    generation = []
    for i in range(size):
        generation.append([])
        for j in range(size):
            comp = random.random()
            generation[i].append(True) if comp < u_bound else generation[i].append(False)

    return generation


def end_message(cnt):
    ''' End function for displaying messages'''
    clear()
    if cnt < 10000:
        print("THEY ALL DIED IN {} ITERATIONS!!!!!".format(cnt))
    else:
        print("They made it. Gosh darn, they all made it after {} iterations".format(cnt))
    print("Thanks for playing.")


def automata(generation, done, cnt, opts):
    if not opts.silent:
        time.sleep(.2)
        clear()
        print_generation(generation)
    generation, deaths = proliferate(generation)
    cnt += 1
    done = deaths if not cnt == 1000 else 0
    return generation, done, cnt


def main(args):

    generation = generation_rand_seed(args.size, args.upper)
    done = 1
    cnt = 0
    while done:
        generation, done, cnt = automata(generation, done, cnt, args)
    end_message(cnt)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description=("It's Conway's game of life! The classic game"
                     " of cellular automata!"))
    parser.add_argument(
        "-sv", "--silent", action='store_true', default=False,
        help=("Run conway's game without any console output"))
    parser.add_argument(
        "-u", "--upper", nargs=1, type=float, help=("Set the "
            "upper bound for the random generation of cells 0 < upper"
            " <= 1."), default=0.2)
    parser.add_argument(
        "-si", "--size", nargs='?', type=int, help=("Set the size of the"
            "scare that you would like the cellular automata to exist "
            "within. Should probably be less than the size of you term"
            "inal but, as of yet, there is no strict restriction on "
            "size"), default=25)
    parser.add_argument(
        "-s", "--seed", nargs=1, type=int, help=("Start conway with "
            "a specific seed to get a certain conway going."))

    return parser.parse_args(args)


if __name__ == "__main__":
    main(parse_args(sys.argv[1:]))
