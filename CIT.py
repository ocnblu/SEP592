import math
import random
import copy
import argparse
import numpy as np


op_reward = np.ones(6)


def combination(t, data):
    ret = []

    if t > 1:
        for k in range(len(data) - t + 1):
            c = combination(t - 1, data[k + 1:])

            for i in range(len(data[k])):
                for j in range(len(c)):
                    ret.append([data[k][i]] + c[j])
    else:
        for i in range(len(data)):
            for j in range(len(data[i])):
                ret.append([data[i][j]])

    return ret


def build_possible_tuple(t, data, constraint):
    tuples = combination(t, data)

    possible_tuple = []

    for tup in tuples:
        is_del = False

        for c in constraint:
            if is_del:
                break

            if c[1][0] in tup:
                if c[0] == '-':
                    is_del = False

                    for i in range(1, len(c[1])):
                        if c[1][i] in tup:
                            is_del = True
                            break
                else:
                    is_del = False

                    dat = copy.deepcopy(data)

                    for d in dat:
                        for i in range(1, len(c[1])):
                            if c[1][i] in d:
                                d.remove(c[1][i])
                                for dd in d:
                                    if dd in tup:
                                        is_del = True
                                        break

        if not is_del:
            possible_tuple.append(tup)

#    print('build:', possible_tuple)

    return possible_tuple


def gen_row(data):
    t = []

    for j in range(len(data)):
        t.append(random.choice(data[j]))

    return t


def initial_array(t, data, n):
    a = []

    for i in range(n):
        a.append(gen_row(data))

    return a


def count_missing_tuple(a):
    count = len(possible_tuple)

    for t in possible_tuple:
        tup = set(t)

        for r in a:
            row = set(r)

            if tup == row.intersection(tup):
                count -= 1
                break

#    print(len(possible_tuple), count)

    return count


def mutation(data, a, r, c):
    l = copy.deepcopy(data[c])
    l.remove(a[r][c])

    a[r][c] = l[random.randint(0, len(l) - 1)]

    return a


def crossover(a, r1, r2):
    for i in range(len(a[r1])):
        if random.uniform(0, 1) < 0.2:
            a[r1][i], a[r2][i] = a[r2][i], a[r1][i]

    return a


def local_move(data, op, a):
    ret = copy.deepcopy(a)
#    print('in: ', ret)

    for i in range(len(op)):
        r1 = random.randint(0, len(ret) - 1)
        r2 = random.randint(0, len(ret) - 1)
        c = random.randint(0, len(ret[r1]) - 1)

#        print(r1, r2, c)

        if op[i] == 0:
#            print('Single Mutation (Std)')

            mutation(data, ret, r1, c)
        elif op[i] == 1:
#            print('Add/Del (Std)')

            del ret[r1]

            ret.append(gen_row(data))
        elif op[i] == 2:
#            print('Multiple Mutation (Std)')

            crossover(ret, r1, r2)
        elif op[i] == 3:
#            print('Single Mutation (Smart)')

            mutation(data, ret, r1, c)
        elif op[i] == 4:
#            print('Add/Del (Smart)')

            del ret[r1]

            ret.append(gen_row(data))
        elif op[i] == 5:
#            print('Multiple Mutation (Smart)')

            crossover(ret, r1, r2)

#    print('out:', ret)

    return ret


def clause_get_random_term(clause):
    return clause[random.randint(1, len(clause) - 1)]


def random_fix_term(row, is_plain, term):
    dat = []

    for d in data:
        if term in d:
            dat = copy.deepcopy(d)
            break

    if len(dat) > 0:
        if not is_plain:
            if term in row:
                dat.remove(term)
                row[row.index(term)] = random.choice(dat)
        else:
            for j in range(len(row)):
                if row[j] in dat:
                    dat.remove(row[j])
                    row[j] = random.choice(dat)

    return row


def fix_cons_violation(a, c):
#    print('fix_cons_violation')
#    has_violation = False

#    print('in: ', has_violation, a)

    for row in a:
        fix_time = 0
        is_restart = True

        while is_restart:
            is_restart = False
            has_violation = False

            for clause in c:
                if clause[1][0] in row:
                    if clause[0] == '-':
                        is_plain = False
                        has_violation = False
                    else:
                        is_plain = True
                        has_violation = True
#                        print('violation0:', row, has_violation)

                    for i in range(1, len(clause[1])):
                        if clause[1][i] in row:
                            if not is_plain:
                                has_violation = True
#                                print('violation1:', row, has_violation)
                            else:
                                has_violation = False
#                                print('violation2:', row, has_violation)
                            break

                    if has_violation:
#                        print('violation3:', row)
                        if fix_time == max_fix_time:
                            break

                        term = clause_get_random_term(clause[1])
                        row = random_fix_term(row, is_plain, term)
#                        print('violation4:', row)
                        fix_time += 1
                        is_restart = True
                        break

    if has_violation:
        print('out:', has_violation, a)

    return has_violation


def rl_agent_choose_action(missing):
    global op_reward

    op = []

    if False:
        '''
        for i in range(6):
            if random.uniform(0, 1) > 0.5:
                op.append(i)
    
        if len(op) == 0:
            op = [random.randint(0, 5)]
    
        random.shuffle(op)
        '''
        op = [random.randint(0, 5)]
#        '''
    else:
        r = random.randint(0, op_reward.sum() - 1)

        for i in range(len(op_reward)):
            if r < op_reward[i]:
                op = [i]
                break
            else:
                r -= op_reward[i]

    return op


def rl_agent_set_reward(op, reward):
    global op_reward

    op_reward[op] += reward
    op_reward -= np.min(op_reward) - 1


def cool(temp):
    return temp * decrement


def cit(t, data, c, n, max_improvement, temp):
    a = initial_array(t, data, n)

    no_improvement = 0
    cnt = 0
    curr_missing = count_missing_tuple(a)

    while max_improvement >= no_improvement:
        cnt += 1

        op = rl_agent_choose_action(curr_missing)
        a_p = local_move(data, op, a)

        while True:
            has_violation = fix_cons_violation(a_p, c)

            if not has_violation:
                break

            a_p = local_move(data, op, a)

        new_missing = count_missing_tuple(a_p)
        d_fitness = curr_missing - new_missing
        rl_agent_set_reward(op, d_fitness)

        if d_fitness > 0 or math.exp(d_fitness / temp) > random.uniform(0, 1):
            if d_fitness == 0:
                no_improvement += 1
            else:
                no_improvement = 0

            a = copy.deepcopy(a_p)
            curr_missing = new_missing
            print(curr_missing)

        if curr_missing == 0 and new_missing == 0 and not has_violation:
            break

        temp = cool(temp)

    # Remove the duplication
    '''
    a = list(set([tuple(set(item)) for item in a]))
    '''
    tmp = []

    for row in a:
        if row not in tmp:
            tmp.append(row)

    a = tmp

    a.sort()

    return a, curr_missing, has_violation, cnt


def open_data_file(name):
    t = 0
    ret = []
    d = 0

    if name is not None:
        f = open(name, 'r')

        t = int(f.readline().strip().rstrip())
        cnt = int(f.readline().strip().rstrip())
        nums = f.readline().strip().rstrip().split(' ')

        for i in range(cnt):
            tmp = []

            for j in range(int(nums[i])):
                tmp.append(d)
                d += 1

            ret.append(tmp)

        f.close()

    return t, ret


def open_const_file(name):
    ret = []

    if name is not None:
        f = open(name, 'r')

        row = int(f.readline().strip().rstrip())

        for i in range(row):
            column = int(f.readline().strip().rstrip())
            dat = f.readline().strip().rstrip().split(' ')

            tmp = []

            for j in range(column):
                tmp.append(int(dat[2 * j + 1]))

            ret.append([dat[2], tmp])

        f.close()

    return ret


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find the covering array.')
    parser.add_argument('name', help='Name of data file to open')
    parser.add_argument('-c', dest='constraint', required=False, default=None,
                        help='Set the name of constraint file')
    parser.add_argument('-n', dest='size', required=False, default=10,
                        help='Set the target size of the covering array (Default: 10)')
    parser.add_argument('-i', dest='improve', required=False, default=256,
                        help='Set the maximum number of non-improvements (Default: 256)')
    parser.add_argument('-f', dest='fix_time', required=False, default=10,
                        help='Set the maximum number of the fix (Default: 10)')
    parser.add_argument('-t', dest='temperature', required=False, default=0.5,
                        help='Set the initial temperature (Default: 0.5)')
    parser.add_argument('-d', dest='decrement', required=False, default=0.9999,
                        help='Set the decremental rate of the temperature (Default: 0.9999)')
    args = parser.parse_args()

    filename = args.name
    constraint_filename = args.constraint
    n = int(args.size)
    max_no_improvement = int(args.improve)
    max_fix_time = int(args.fix_time)
    temperature = float(args.temperature)
    decrement = float(args.decrement)

    '''
    t = 3
    n = 14
    max_fix_time = 10

    data = [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9, 10]]
    constraint = [['-', [0, 8]], ['+', [3, 4, 7]]]
    '''

#    n=18
#    max_no_improvement=256

    print('Data File:               ', filename)
    print('Constraint File:         ', constraint_filename)
    print('Size of Covering Array:  ', n)
    print('Max number of no improve:', max_no_improvement)
    print('Max number of fix try:   ', max_fix_time)
    print('Initial Temperature:     ', temperature)
    print('Decrease rate of Temp.:  ', decrement)

    t, data = open_data_file(filename)
    constraint = open_const_file(constraint_filename)

    print('Strength of the array;   ', t)
    print()

    possible_tuple = build_possible_tuple(t, data, constraint)
    solution, missing, violation, iteration = cit(t, data, constraint, n, max_no_improvement, temperature)

    print('Number of Missing Tuples:', missing)
    print('Constraint Violation:    ', violation)
    print('No of iterations:        ', iteration)
    print()

    for i in range(len(solution)):
        print(i + 1, list(solution[i]))