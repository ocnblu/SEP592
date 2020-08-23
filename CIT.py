import math
import random
import copy
import argparse
import numpy as np
from operator import itemgetter


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


def insert_constraint(cnst, val):
    ret = False

    if val not in cnst:
        cnst.append(val)
        ret = True

    return ret


def build_possible_tuple(t, data, constraint):
    tuples = combination(t, data)

    possible_tuple = []

    is_change = True

    while is_change:
        is_change = False

        for i in range(len(constraint)):
            for j in range(i + 1, len(constraint)):
                if constraint[i][0] == constraint[j][0]:
                    if constraint[i][1][0] == constraint[j][1][0]:
                        c1 = constraint[i][1][1]
                        c2 = constraint[j][1][1]
                    elif constraint[i][1][1] == constraint[j][1][0]:
                        c1 = constraint[i][1][0]
                        c2 = constraint[j][1][1]
                    elif constraint[i][1][0] == constraint[j][1][1]:
                        c1 = constraint[i][1][1]
                        c2 = constraint[j][1][0]

                if c1 > c2:
                    c1, c2 = c2, c1

                is_change = insert_constraint(constraint, [constraint[i][0], [c1, c2]])

        constraint = sorted(constraint, key=itemgetter(1))

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

        possible_tuple.append([tup, not is_del])

    return possible_tuple


def gen_row(data):
    ret = []

    for j in range(len(data)):
        ret.append(random.choice(data[j]))

    return ret


def initial_array(t, data, n):
    ret = []

    for i in range(n):
        ret.append(gen_row(data))

    return ret


def count_missing_tuple(a):
    count = 0

    for t in possible_tuple:
        tup = set(t[0])
        is_exist = t[1]

        is_count = is_exist

        for r in a:
            row = set(r)

            if tup == row.intersection(tup):
                is_count = not is_exist

        if is_count:
            count += 1

    return count


def mutation(dat, a, r, c):
    l = copy.deepcopy(dat[c])
    l.remove(a[r][c])

    a[r][c] = random.choice(l)

    return a


def crossover(a, r1, r2):
    for i in range(len(a[r1])):
        if random.uniform(0, 1) < 0.2:
            a[r1][i], a[r2][i] = a[r2][i], a[r1][i]

    return a


def get_missing_tuple(a):
    ret = []

    for r in a:
        row = set(r)

        for t in possible_tuple:
            tup = set(t[0])
            is_required = t[1]

            if tup != row.intersection(tup) and is_required:
                ret.append(r)
                break
            elif tup == row.intersection(tup) and not is_required:
                ret.append(r)
                break

    return ret


def smart_mutation(data, a, r, c):
    missing = get_missing_tuple(a)

    if len(missing) == 0:
        a = mutation(data, a, r, c)
    else:
        m = random.choice(missing)

        for i in range(len(a)):
            if a[i] == m:
                c = random.randint(0, len(a[i]) - 1)
                l = copy.deepcopy(data[c])
                l.remove(a[i][c])

                a[i][c] = random.choice(l)

    return a


def smart_crossover(data, a, r1, r2):
    missing = get_missing_tuple(a)

    if len(missing) > 0:
        row1 = random.choice(missing)
        row2 = random.choice(missing)

        for i in range(len(a)):
            if a[i] == row1:
                r1 = i
            elif a[i] == row2:
                r2 = i

    return crossover(a, r1, r2)


def local_move(data, op, a):
    ret = copy.deepcopy(a)

    for i in range(len(op)):
        r1 = random.randint(0, len(ret) - 1)
        r2 = random.randint(0, len(ret) - 1)
        c = random.randint(0, len(ret[r1]) - 1)

        if op[i] == 0:
            # Single Mutation (Std)

            ret = mutation(data, ret, r1, c)
        elif op[i] == 1:
            # Add/Del (Std)

            del ret[r1]

            ret.append(gen_row(data))
        elif op[i] == 2:
            # Multiple Mutation (Std)

            ret = crossover(ret, r1, r2)
        elif op[i] == 3:
            # Single Mutation (Smart)

            ret = smart_mutation(data, a, r1, c)
        elif op[i] == 4:
            # Add/Del (Smart)

            missing = get_missing_tuple(a)

            if len(missing) > 0:
                m = random.choice(missing)

                for i in range(len(a)):
                    if a[i] == m:
                        r1 = i
                        break

            del ret[r1]

            ret.append(gen_row(data))
        elif op[i] == 5:
            # Multiple Mutation (Smart)

            ret = smart_crossover(data, a, r1, r2)

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
    has_violation = False

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

                    for i in range(1, len(clause[1])):
                        if clause[1][i] in row:
                            if not is_plain:
                                has_violation = True
                            else:
                                has_violation = False
                            break

                    if has_violation:
                        if fix_time == max_fix_time:
                            break

                        term = clause_get_random_term(clause[1])
                        row = random_fix_term(row, is_plain, term)

                        fix_time += 1
                        is_restart = True
                        break

    return has_violation


def rl_agent_choose_action(missing):
#    return [random.randint(0, 5)]
    return [random.randint(0, 2)]


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
    has_violation = False

    while max_improvement >= no_improvement:
        cnt += 1

        op = rl_agent_choose_action(curr_missing)
        a_p = local_move(data, op, a)

        while True:
            has_violation = fix_cons_violation(a_p, c)

            if not has_violation:
                break

            op = rl_agent_choose_action(curr_missing)
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

        if curr_missing == 0 and new_missing == 0 and not has_violation:
            break

        temp = cool(temp)

    # Remove the duplication
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

    try:
        f = open(name, 'r')
    except:
        print('Constraints file is NOT found.')
        return ret

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


def save_solution(name, sol):
    f = open(name, 'w+')

    f.write(str(len(sol)) + '\n')

    for s in sol:
        for num in s:
            f.write(str(num) + ' ')
        f.write('\n')

    f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find the covering array.')
    parser.add_argument('model_name', help='Name of model file to open (w/o extension)')
    parser.add_argument('-n', dest='size', required=False, default=10,
                        help='Set the target size of the covering array (Default: 10)')
    parser.add_argument('-i', dest='improve', required=False, default=256,
                        help='Set the maximum number of non-improvements (Default: 256)')
    parser.add_argument('-f', dest='fix_time', required=False, default=0,
                        help='Set the maximum number of the fix (Default: 0)')
    parser.add_argument('-t', dest='temperature', required=False, default=0.5,
                        help='Set the initial temperature (Default: 0.5)')
    parser.add_argument('-d', dest='decrement', required=False, default=0.9999,
                        help='Set the decremental rate of the temperature (Default: 0.9999)')
    args = parser.parse_args()

    filename = args.model_name + '.citmodel'
    constraint_filename = args.model_name + '.constraints'
    output_filename = args.model_name + '.coveringarray'
    n = int(args.size)
    max_no_improvement = int(args.improve)
    max_fix_time = int(args.fix_time)
    temperature = float(args.temperature)
    decrement = float(args.decrement)

    print('Model File:              ', filename)
    print('Constraint File:         ', constraint_filename)
    print('Size of Covering Array:  ', n)
    print('Max number of no improve:', max_no_improvement)
    print('Max number of fix try:   ', max_fix_time)
    print('Initial Temperature:     ', temperature)
    print('Decrease rate of Temp.:  ', decrement)

    t, data = open_data_file(filename)
    constraint = open_const_file(constraint_filename)

    max_data = 0

    for d in data:
        max_data = max(max_data, max(d))

    print('Strength of the array:   ', t)
    print()

    possible_tuple = build_possible_tuple(t, data, constraint)
    solution, missing, violation, iteration = cit(t, data, constraint, n, max_no_improvement, temperature)

    print('Number of Missing Tuples:', missing)
    print('Constraint Violation:    ', violation)
    print('No of iterations:        ', iteration)
    print()

    for i in range(len(solution)):
        print(i + 1, list(solution[i]))

    save_solution(output_filename, solution)
