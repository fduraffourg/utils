#!/bin/env python
import random


CHIFFRES = (1,2,3,4,5,6,7,8,9,10,1,2,3,4,5,6,7,8,9,10,25,50,75,100)

def new_game():
    numbers = random.sample(CHIFFRES, 6)
    res = random.randint(100,999)
    return res, numbers


def list_operate(path, test_keep, fo, operande, rev=False):
    paths = []
    for i in range(1,len(path)):
        new_path = []

        if not rev:
            a,b = path[0], path[i]
        else:
            a,b = path[i], path[0]

        if not test_keep(a[0],b[0]):
            continue

        new_path += [(fo(a[0], b[0]),
                (a[1], operande, b[1]))]

        for p, v in enumerate(path):
            if p != i and p != 0:
                new_path.append(v)

        paths.append(new_path)

    return(paths)


def solve_iter(res, path):
    if len(path) == 1:
        return path[0]

    paths = []

    paths += list_operate(path, lambda a,b: True, lambda a,b:a+b, '+', False)
    paths += list_operate(path, lambda a,b: a-b>0, lambda a,b:a-b, '-', False)
    paths += list_operate(path, lambda a,b: a-b>0, lambda a,b:a-b, '-', True)
    paths += list_operate(path, lambda a,b: a!=1 and b!=1 , lambda a,b:a*b, 'x', False)
    paths += list_operate(path, lambda a,b: a%b==0 and b!=1, lambda a,b:int(a/b), '/', False)
    paths += list_operate(path, lambda a,b: a%b==0 and b!=1, lambda a,b:int(a/b), '/', True)
    
    best = (999,)

    for p in paths:
        if p[0][0] == res:
            return p[0]

        s = solve_iter(res, p)
        if s[0] == res:
            return s

        if abs(s[0] - res) < abs(best[0] - res):
            best = s

    return best

def solve(res, numbers):
    path = [(x,x) for x in numbers]

    solution = solve_iter(res, path)

    print(solution)
    


if __name__ == "__main__":
    game = new_game()
    print(game)
    solve(*game)
