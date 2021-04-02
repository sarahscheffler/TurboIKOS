import sys, csv, math, os
from subprocess import *

ex = Popen(["python3", "mergedTest.py", "circuits/matmult_2.pws"], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
print(ex.stdout.readline())
print(ex.stdout.readline())
ex.stdin.write(b'3\n')
ex.stdin.write(b'80\n')
print(ex.communicate(b"n\n")[0])


num_parties = [3, 10, 64]
soundness = [128, 80, 40]
rows = [4, 8, 16, 32, 64, 128]

with open('TurboIKOS-tests-output.csv', mode='w') as csv_file:
    fieldnames = ['num parties', 'soundness level', 'num repetitions', 'rows of matrix', 'columns of matrix', 'proof size', 'prover runtime', 'verifier runtime']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    empty_dict = {'num parties': 0, 'soundness level': 0, 'num repetitions': 0, 'rows of matrix': 0, 'columns of matrix': 0, 'proof size': 0, 'prover runtime': 0, 'verifier runtime': 0}

    for n in num_parties: 
        for s in soundness:
            for r in rows: 
                dict_copy = empty_dict
                reps = math.ceil(128/math.log2(n))
                col = r*2

                command = Popen(["python3, "])

                command = Popen(["python3", "mergedTest.py", "circuits/matmult_2.pws"], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
                command.stdin.write(b'%i\n' % n)
                command.stdin.write(b'%i\n' % reps)


    writer.writeheader()
    writer.writerow(empty_dict)


# with open('reverie-tests-output.csv', mode='w') as csv_file:
#     fieldnames = ['num parties', 'soundness level', 'num repetitions', 'rows of matrix', 'columns of matrix', 'proof size', 'prover runtime', 'verifier runtime']
#     writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

#     empty_dict = {'num parties': 3, 'soundness level': 0, 'num repetitions': 0, 'rows of matrix': 0, 'columns of matrix': 0, 'proof size': 0, 'prover runtime': 0, 'verifier runtime': 0}

#     writer.writeheader()
#     writer.writerow(empty_dict)

