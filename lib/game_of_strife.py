#!/usr/bin/env python3

import copy
import os
import sys
import random
import time

''' Conway's Game of Life '''


def Check_Neighbors(Live_List, i, j):
    ''' Logic for adding up the neighbors of a particular cell '''

    neighbors = 0

    # Middle Pieces
    if 0 < i < len(Live_List)-1 and 0 < j < len(Live_List[i])-1:
        for k in range(-1,2):
            neighbors += sum(Live_List[i+k][j-1:j+2])
        neighbors -= Live_List[i][j]

    # Top Piece
    elif i == 0 and 0 < j < len(Live_List[i])-1:
        for k in range(0,2):
            neighbors += sum(Live_List[i+k][j-1:j+2])
        neighbors += sum(Live_List[-1][j-1:j+2])
        neighbors -= Live_List[i][j]

    # Bottom Piece
    elif i == len(Live_List)-1 and 0 < j < len(Live_List[i])-1:
        for k in range(-1,1):
            neighbors += sum(Live_List[i+k][j-1:j+2])
        neighbors += sum(Live_List[0][j-1:j+2])
        neighbors -= Live_List[i][j]

    # Left Side
    elif 0 < i < len(Live_List)-1 and j == 0:
        for k in range(-1,2):
            neighbors += sum(Live_List[i+k][j:j+2])
            neighbors += Live_List[i+k][-1]
        neighbors -= Live_List[i][j]

    # Right Side
    elif 0 < i < len(Live_List)-1 and j == len(Live_List[i])-1:
        for k in range(-1,2):
            neighbors += sum(Live_List[i+k][j-1:j+1])
            neighbors += Live_List[i+k][0]
        neighbors -= Live_List[i][j]

    # Top Left Corner
    elif i == 0 and j == 0:
        neighbors += Live_List[i][j+1] + Live_List[i+1][j+1] + Live_List[i+1][j]
        neighbors += Live_List[i][-1] + Live_List[-1][-1] + Live_List[-1][j]

    # Top Right Corner
    elif i == 0 and j == len(Live_List[i])-1:
        neighbors += Live_List[i][j-1] + Live_List[i+1][j-1] + Live_List[i+1][j]
        neighbors += Live_List[i][0] + Live_List[-1][-1] + Live_List[-1][j]

    # Bottom Right Corner
    elif i == len(Live_List)-1 and j == len(Live_List[i])-1:
        neighbors += Live_List[i][j-1] + Live_List[i-1][j-1] + Live_List[i-1][j]
        neighbors += Live_List[0][0] + Live_List[-1][0] + Live_List[0][-1]

    # Bottom Left Corner
    elif i ==len(Live_List)-1 and j == 0:
        neighbors += Live_List[i][j+1] + Live_List[i-1][j+1] + Live_List[i-1][j]
        neighbors += Live_List[0][j] + Live_List[-1][-1] + Live_List[0][-1]

    return neighbors


def Proliferate(Cur_Gen):
    ''' Compute the death and life of my little cell minions!!!'''

    # Make a deep copy to return afterwards (Can't change while iterating)
    Next_Gen = [[False for i in  j] for j in Cur_Gen]
    Death_Count = 0

    for ind, row in enumerate(Cur_Gen):
        for jind, col in enumerate(row):
            neighbors = Check_Neighbors(Cur_Gen, ind, jind)

            if (col and neighbors < 2) or (col and neighbors > 3):
                Next_Gen[ind][jind] = False
            if ((neighbors == 3 or neighbors == 2) and col == True):
                Next_Gen[ind][jind] = True
            if not col and neighbors == 3:
                Next_Gen[ind][jind] = True

        Death_Count += sum(Next_Gen[ind])

    return Next_Gen, Death_Count


def keep_Gens(Cur_Gen, count):
    ''' Keep the generations instead of throwing them out '''
    end = 0
    Gen_List = []
    while end < count:
        Gen_List.append(Cur_Gen)
        Next_Gen, Death = Proliferate(Cur_Gen)
        there, Gen = repetition_look(Gen_List)
        if there == True or not Death:
            end = count
    return Gen


def repetition_look(Gen_List):
    ''' Check if the generation was there previously '''
    if Gen_List[-1] in Gen_List[:-1]:
        return True, Gen_List[-1]
    else:
        return False, []

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def Print_Gen(Gen):
    ''' Print Generation to screen '''
    for row in Gen:
        print("".join(["& " if col else "  " for col in row]))

def potential_seed(size=30, u_bound=0.2, tries=40, time=50):
    Good_seeds = []
    for i in range(tries):
        Gen = gen_rand_seed(size, u_bound)
        potent_seed = keep_Gens(Gen)
        if potent_seed:
            Good_seeds.append(potent_seed)
    return Good_seeds

def gen_rand_seed(size, u_bound):
    ''' Generate a randome seed for the Game '''
    Gen = []
    for i in range(size):
        Gen.append([])
        for j in range(size):
            comp = random.random()
            Gen[i].append(True) if comp < u_bound else Gen[i].append(False)

    return Gen

def end_message(cnt):
    ''' End function for displaying messages'''
    clear()
    if cnt < 10000:
        print("THEY ALL DIED IN {} ITERATIONS!!!!!".format(cnt))
    else:
        print("They made it. Gosh darn, they all made it after {} iterations".format(cnt))
    print("Thanks for playing.")

def automata(Gen, done, cnt, opts):
    if not opts.silent:
        time.sleep(.2)
        clear()
        Print_Gen(Gen)
    Gen, Death= Proliferate(Gen)
    done = Death
    cnt += 1
    if cnt == 1000: done = 0
    return Gen, done, cnt

def main():
    opts = parse_args()
    print(vars(opts))
    return

    Gen = gen_rand_seed(opts.size, opts.upper)
    done = 1
    cnt = 0
    while done:
        Gen, done, cnt = automata(Gen, done, cnt, opts)
    end_message(cnt)



def parse_args():
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
        "-si", "--size", nargs=1, type=int, help=("Set the size of the"
            "scare that you would like the cellular automata to exist "
            "within. Should probably be less than the size of you term"
            "inal but, as of yet, there is no strict restriction on "
            "size"), default=25)
    parser.add_argument(
        "-s", "--seed", nargs=1, type=int, help=("Start conway with "
            "a specific seed to get a certain conway going."))
    opts = parser.parse_args()
    return opts

if __name__ == "__main__":
    # The hackiest fucking way of doing this
    try:
        args = (i for i in sys.argv[1:])
        read_args(*args)
    except TypeError:
        default_ret()

    sys.exit(0)
