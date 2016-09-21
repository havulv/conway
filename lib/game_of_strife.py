#!/usr/bin/python3.5

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


def Proliferate(Cur_Gen, neigh_array=[]):
    ''' Compute the death and life of my little cell minions!!!'''

    # Make a deep copy to return afterwards (Can't change while iterating)
    Next_Gen = [[False for i in  j] for j in Cur_Gen]
    Death_Count = 0

    for i in range(len(Cur_Gen)):
        for j in range(len(Cur_Gen[i])):
            # I am arguing that it is okay to pass this list in so many times
            # because the list is a shared object so I am only creating and
            # destroying a reference each time the function is called
            neighbors = Check_Neighbors(Cur_Gen, i, j)

            if (Cur_Gen[i][j] == True and neighbors < 2) or (Cur_Gen[i][j] == True and neighbors > 3):
                Next_Gen[i][j] = False
            if ((neighbors == 3 or neighbors == 2) and Cur_Gen[i][j] == True):
                Next_Gen[i][j] = True
            if Cur_Gen[i][j] == False and neighbors == 3:
                Next_Gen[i][j] = True

        Death_Count += sum(Next_Gen[i])

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

    for i in range(len(Gen)):
        for j in range(len(Gen[i])):
            if Gen[i][j]:
                print("& ", end="")
            else:
                print("  ", end="")
        print("")
    print("")


def main_search(size=30, u_bound=0.2, tries=40, time=50):
    Good_seeds = []
    for i in range(tries):
        Gen = gen_rand_seed(size, u_bound)
        potent_seed = keep_Gens(Gen)
        if potent_seed:
            Good_seeds.append(potent_seed)
    return Good_seeds

def main_seed(Gen, u_bound=0.2):
    ''' Run through visuals with a set seed '''
    done = 1
    cnt = 0
    clear()
    Print_Gen(Gen)
    while done:
        time.sleep(.3)
        Gen, Death = Proliferate(Gen)
        Print_Gen(Gen)
        clear()
        done = Death
        cnt += 1
        if cnt == 1000: done = 0
    clear()
    end_message(cnt)


def main_vis(size=30, u_bound=0.2):
    ''' Print, clear screen and loop until resolution '''

    Gen = gen_rand_seed(size, u_bound)
    neigh_array = Gen
    done = 1
    cnt = 0
    while done:
        time.sleep(.2)
        clear()
        Print_Gen(Gen)
        Gen, Death= Proliferate(Gen)
        done = Death
        cnt += 1
        if cnt == 1000: done = 0
    end_message(cnt)


def main_silent(size=50, u_bound=0.2):
    ''' A main function for conway's game of life running in the background '''

    Gen = gen_rand_seed(size, u_bound)

    cnt = 0
    done = 1

    while done:
        Gen, Death = Proliferate(Gen)
        done = Death
        cnt += 1
        if cnt == 10000: done = 0
    end_message(cnt)


def invalid(): print("Invalid input. Try again or do something else with your time")


def default_ret():
    ''' Trying for functionality... '''
    for i in [["-v", "[optional: size={mat_size}", "ub={upper bound}]",  "Visual Conway"],
                      ["-s", "[optional: size={mat_size}", "ub={upper bound}]", "Background Conway"]]:
        print("{0} -- {1} -- {2} -- {3}".format(i[0], i[1], i[2],i[3]))


def read_args(arg1, arg2="", arg3=""):
    ''' Read in the system arguments associated at runtime '''
    if arg1 == "-s":
        check_optionals(main_silent, arg2, arg3)

    elif arg1 == "-v":
        check_optionals(main_vis, arg2, arg3)

    else:
        default_ret()


def check_optionals(main, arg2, arg3):
    ''' I'm trying to be a functional programmer '''
    if arg2[0:4] == "size":
        if arg3[0:2] == "ub":
            main(int(arg2[5:]), float(arg3[3:]))
        else:
            main(size=int(arg2[5:]))
    else:
        main()


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


if __name__ == "__main__":
    # The hackiest fucking way of doing this
    try:
        args = (i for i in sys.argv[1:])
        read_args(*args)
    except TypeError:
        default_ret()

    sys.exit(0)
