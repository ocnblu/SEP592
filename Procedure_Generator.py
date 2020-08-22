import argparse
from datetime import datetime


def open_csv_file(name):
    ret = []

    f = open(name, 'r')

    while True:
        line = f.readline().strip().rstrip()

        if not line: break

        ret.append(line.split(','))

    f.close()

    return ret


def parse_cmd(data):
    ret = []

    for d in data:
        mnemonic = d[0]
        description = d[1]
        tlm = d[2]
        status = d[3]

        ret.append([mnemonic, tlm, status])

    del ret[0]

    return ret


def parse_tlm(data):
    ret = []

    for i in range(1, len(data)):
        mnemonic = data[i][0]
        status = []

        default = int(data[i][2])

        for j in range(3):
            if len(data[i][3 + j]) > 0:
                status.append(data[i][3 + j])
            else:
                break

        ret.append([mnemonic, status, default])

    return ret


def get_status(data, mnemonic):
    for d in data:
        if d[0] == mnemonic:
            return d[1]


def get_command(cmd, tlm, status):
    ret = None

    for c in cmd:
        if c[1] == tlm and c[2] == status:
            ret = c[0]
            break

    return ret


def get_index(tlm, mnemonic, num):
    ret = num

    for m in mnemonic:
        for t in tlm:
            if m == t[0]:
                if ret >= len(t[1]):
                    ret -= len(t[1])
                else:
                    return ret

                break

    return ret


def get_default(tlm, mnemonic):
    ret = -1

    for t in tlm:
        if t[0] == mnemonic:
            ret = t[1][t[2]]

    if ret == -1:
        print('ERROR: ' + mnemonic + ' does NOT have the default status.')

    return ret


def parse_chunk(chunk):
    num = 0
    constraint = []
    mnemonic = []

    if chunk[0][0] == 'Test Title':
        title = chunk[0][1].replace(' ', '_')

    if chunk[1][0] == 'Mnemonic':
        for i in range(1, len(chunk[1])):
            num = i

            if len(chunk[1][i]) > 0:
                mnemonic.append(chunk[1][i])
            else:
                break

    if chunk[2][0] == 'Value':
        for i in range(1, num):
            constraint.append([[mnemonic[i - 1], chunk[2][i]]])

    for j in range(3, len(chunk), 2):
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


def open_ca_file(name):
    ret = []

    f = open(name, 'r')

    num = int(f.readline().strip().rstrip())

    for i in range(num):
        ret.append(f.readline().strip().rstrip().split(' '))

    f.close()

    return ret


def generate_procedure(ca, c, case, cmd, tlm):
    ret = []

    test = case[c]
    title = test[0]
    mnemonic = test[1]
    constraint = test[2]

    ret.append([None, '================================================================================'])
    ret.append([None, ''])
    ret.append([None, '\tTITLE: Procedure for ' + title])
    ret.append([None, '\tAUTHOR: Covering Array Tool'])
    ret.append([None, '\tFILE GENERATED DATE: ' + datetime.today().strftime('%Y-%m-%d')])
    ret.append([None, '\tLAST MODIFIED DATE:  ' + datetime.today().strftime('%Y-%m-%d')])
    ret.append([None, ''])
    ret.append([None, '\tHISTORY'])
    ret.append([None, '\t 1. ' + datetime.today().strftime('%Y-%m-%d') + ' INITIAL'])
    ret.append([None, ''])
    ret.append([None, '================================================================================'])
    ret.append([None, ''])
    ret.append([None, '--------------------------------------------------------------------------------'])
    ret.append([None, ' * Check default status'])
    ret.append([None, '--------------------------------------------------------------------------------'])
    ret.append([None, ''])

    for m in mnemonic:
        ret.append([True, 'Check ' + m + '.'])
        ret.append([False, '  - Expected: ' + get_default(tlm, m)])
        ret.append([False, '  - Observed: ______________________________'])
        ret.append([None, ''])

    for i in range(len(ca)):
        ret.append([None, '--------------------------------------------------------------------------------'])
        ret.append([None, ' * Check Test Case ' + str(i + 1)])
        ret.append([None, '--------------------------------------------------------------------------------'])
        ret.append([None, ''])

        for j in range(len(mnemonic) - 1, -1, -1):
            m = mnemonic[j]
            idx = get_index(tlm, mnemonic, int(ca[i][j]))
            ret.append([True, 'Send ' + get_command(cmd, m, get_status(tlm, m)[idx]) + '.'])
            ret.append([None, ''])
            ret.append([True, 'Check ' + mnemonic[j] + '.'])
            ret.append([False, '  - Expected: ' + get_status(tlm, m)[idx]])
            ret.append([False, '  - Observed: ______________________________'])
            ret.append([None, ''])

    ret.append([None, '--------------------------------------------------------------------------------'])
    ret.append([None, ' * Check default status'])
    ret.append([None, '--------------------------------------------------------------------------------'])
    ret.append([None, ''])

    for j in range(len(mnemonic) - 1, -1, -1):
        m = mnemonic[j]
        ret.append([True, 'Send ' + get_command(cmd, m, get_default(tlm, m)) + '.'])
        ret.append([None, ''])

    for m in mnemonic:
        ret.append([True, 'Check ' + m + '.'])
        ret.append([False, '  - Expected: ' + get_default(tlm, m)])
        ret.append([False, '  - Observed: ______________________________'])
        ret.append([None, ''])

    ret.append([None, '================================================================================'])

    return ret


def save_procedure(name, proc):
    print('Output File:', name)
    
    line = 1

    f = open(name, 'w+')

    for row in proc:
        if row[0] is None:
            f.write(row[1] + '\n')
        elif not row[0]:
            f.write('\t' + row[1] + '\n')
        else:
            lno = len(str(line))
            s = str(line) + '.' + ' ' * (3 - lno) + row[1]
            l = len(s)
            is_first = True

            while True:
                if l > 70:
                    if is_first:
                        f.write(s[:70] + ' [       ]\n')
                        is_first = False
                    else:
                        f.write(s[:70] + '\n')
                    s = s[70:]
                    l = len(s)
                else:
                    if is_first:
                        s += ' ' * (70 - l) + ' [       ]'
                    break

            f.write(s + '\n')
            line += 1

    f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate the code for the satellite test.')
    parser.add_argument('ca_name', help='Name of covering array file to open (w/o extension)')
    parser.add_argument('case_name', help='Name of test case file to open')
    parser.add_argument('cmd_name', help='Name of telemetry file to open')
    parser.add_argument('tlm_name', help='Name of telemetry file to open')
    parser.add_argument('-c', dest='testcase', required=False, default=1,
                        help='Set the test case to generate (Default: 1)')
    parser.add_argument('-o', dest='output', required=False, default=None,
                        help='Set the name of output file')
    args = parser.parse_args()

    c = int(args.testcase) - 1
    ca = open_ca_file(args.ca_name + '.coveringarray')
    case = parse_case(open_csv_file(args.case_name))
    cmd = parse_cmd(open_csv_file(args.cmd_name))
    tlm = parse_tlm(open_csv_file(args.tlm_name))

    procedure = generate_procedure(ca, c, case, cmd, tlm)

    save_procedure(args.ca_name + '.txt', procedure)
