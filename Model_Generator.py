import argparse


def open_csv_file(name):
    ret = []

    f = open(name, 'r')

    while True:
        line = f.readline().strip().rstrip()

        if not line: break

        ret.append(line.split(','))

    f.close()

    return ret


def parse_tlm(data):
    ret = []

    for i in range(1, len(data)):
        mnemonic = data[i][0]
        status = []

        for j in range(3):
            if len(data[i][2 + j]) > 0:
                status.append(data[i][2 + j])
            else:
                break

        ret.append([mnemonic, status])

    return ret


def get_status(data, mnemonic):
    for d in data:
        if d[0] == mnemonic:
            return d[1]


def parse_chunk(chunk):
    num = 0

    if chunk[0][0] == 'Test Title':
        title = chunk[0][1]

    if chunk[1][0] == 'Mnemonic':
        mnemonic = []
        for i in range(1, len(chunk[1])):
            num = i

            if len(chunk[1][i]) > 0:
                mnemonic.append(chunk[1][i])
            else:
                break

    constraint = []

    if chunk[2][0] == 'Constraint' and chunk[2 + 1][0] == 'Constraint Value':
        for i in range(1, num):
            constraint.append([[chunk[2][i], chunk[2 + 1][i]]])

    for j in range(4, len(chunk), 2):
        if chunk[j][0] == 'Constraint' and chunk[j + 1][0] == 'Constraint Value':
            for i in range(1, num):
                constraint[i - 1].append([chunk[j][i], chunk[j + 1][i]])

    return [title, mnemonic, constraint]


def parse_case(data):
    ret = []
    chunk = []

    for row in data:
        if len(row[0]) == 0:
            if len(chunk) > 0:
                ret.append(parse_chunk(chunk))
                chunk = []
            else:
                break
        else:
            chunk.append(row)

    if len(chunk) > 0:
        ret.append(parse_chunk(chunk))

    return ret


def generate_model(s, case, tlm):
    models = []
    constraints = []
    num = 0
    dic = []

    for c in case:
        if s > len(c[1]):
            print('Error:', c[0], 'is smaller than the strength:', s)
            break

        mdl = [c[0], s]

        mnemonic = c[1]
        state = []

        for m in mnemonic:
            l = len(get_status(tlm, m))
            state.append(l)
            dic.append([m, num])
            num += l

        mdl.append(len(state))
        mdl.append(state)

        models.append(mdl)

    for c in case:
        mnemonic = c[1]
        cnst = [c[0]]

        for i in range(len(c[2])):
            follower = []

            for con in c[2][i]:
                if len(con[0]) > 0 and len(con[1]) > 0:
                    idx = get_status(tlm, con[0]).index(con[1])
                    follower.append(' + ' + str(dic[mnemonic.index(con[0])][1] + idx))

            if len(follower) > 0:
                cnst.append(['- ' + str(dic[i][1])] + follower)

        constraints.append(cnst)

    return models, constraints


def save_model(prefix, mdl):
    for m in mdl:
        if prefix is None:
            name = m[0] + '.citmodel'
        else:
            name = prefix + m[0] + '.citmodel'

        f = open(name, 'w+')

        f.write(str(m[1]) + '\n')
        f.write(str(m[2]) + '\n')

        for num in m[3]:
            f.write(str(num) + ' ')

        f.close()


def save_constraint(prefix, cnst):
    for c in cnst:
        if len(c) > 1:
            if prefix is None:
                name = c[0] + '.constraints'
            else:
                name = prefix + c[0] + '.constraints'

            f = open(name, 'w+')

            f.write(str(len(c) - 1) + '\n')
            for i in range(1, len(c)):
                f.write(str(len(c[i])) + '\n')

                for j in range(len(c[i])):
                    f.write(str(c[i][j]))

                f.write('\n')

            f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate the model for the covering array.')
    parser.add_argument('case_name', help='Name of test case file to open')
    parser.add_argument('telemetry_name', help='Name of telemetry file to open')
    parser.add_argument('-s', dest='strength', required=True, default=2,
                        help='Set the strength of the covering array (Default: 2)')
    parser.add_argument('-o', dest='prefix', help='Prefix of output file')
    args = parser.parse_args()

    s = int(args.strength)

    case = parse_case(open_csv_file(args.case_name))
    tlm = parse_tlm(open_csv_file(args.telemetry_name))

    model, constraints = generate_model(s, case, tlm)

    save_model(args.prefix, model)
    save_constraint(args.prefix, constraints)

