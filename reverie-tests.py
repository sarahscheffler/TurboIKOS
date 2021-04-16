import sys, csv, math, os
from subprocess import *
from os import path

# ex = Popen(["python3", "testing.py", "circuits/matmult_2.pws"], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
# ex.stdin.write(b'3\n')
# ex.stdin.write(b'80\n')
# out = ex.communicate(b"n\n")[0]
# out = out.split(b'\n')
# print(out)
# Popen(["python3", "matrix_gen.py", "--row", "4", "--col", "8"])

num_parties = [3, 10, 64]
soundness = [128, 80, 40]
rows = [4, 8, 16, 32, 64, 128]

# with open('TurboIKOS-tests-output.csv', mode='w') as csv_file:
#     fieldnames = ['num parties', 'soundness level', 'num repetitions', 'rows of matrix', 'columns of matrix', 'proof size', 'prover runtime', 'verifier runtime']
#     writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#     writer.writeheader()

#     empty_dict = {'num parties': 0, 'soundness level': 0, 'num repetitions': 0, 'rows of matrix': 0, 'columns of matrix': 0, 'proof size': 0, 'prover runtime': 0, 'verifier runtime': 0}

#     for n in num_parties: 
#         for s in soundness:
#             for r in rows: 
#                 reps = math.ceil(128/math.log2(n))
#                 c = r*2

#                 if not path.isfile("circuits/matmult_%ix%i.txt" % (r,c)):
#                     x = Popen(["python3", "matrix_gen.py", "--row", str(r), "--col", str(c)])

#                 command = Popen(["python3", "testing.py", "circuits/matmult_%ix%i.txt" % (r, c)], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
#                 command.stdin.write(b'%i\n' % n)
#                 command.stdin.write(b'%i\n' % reps)
#                 out = command.communicate(b"n\n")[0]
#                 print(out.decode().split('\n'))
#                 outputs = out.decode().split('\n')[-2]
#                 print(outputs)

#                 fill_dict = {'num parties': n, 'soundness level': 0, 'num repetitions': reps, 'rows of matrix': r, 'columns of matrix': c, 'proof size': outputs[b'proof size'], 'prover runtime': outputs[b'prover time'], 'verifier runtime': outputs[b'verifier time']}
#                 writer.writerow(fill_dict)


with open('LZKP-tests-output.csv', mode='w') as csv_file:
    fieldnames = ['num parties', 'soundness level', 'num repetitions', 'rows of matrix', 'columns of matrix', 'proof size', 'prover runtime', 'verifier runtime']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    empty_dict = {'num parties': 0, 'soundness level': 0, 'num repetitions': 0, 'rows of matrix': 0, 'columns of matrix': 0, 'proof size': 0, 'prover runtime': 0, 'verifier runtime': 0}

    for n in num_parties: 
        for s in soundness:
            for r in rows:
                reps = math.ceil(128/math.log2(n))
                c = r*2

                p_command = Popen(['./LZKP', '-p', '1', '-i', '--port', '3000', '-x', '1', '-q', '61', '-M', '2', '-t', str(n-1), '-N', str(n), '-n', str(r), '-m', str(c)], stdout=PIPE, stdin=PIPE, stderr=STDOUT)    
                v_command = Popen(['./LZKP', '-p', '1', '--ip', '127.0.0.1', '--port', '3000', '-x', '1', '-q', '61', '-M', '2', '-t', str(n-1), '-N', str(n), '-n', str(r), '-m', str(c)], stdout=PIPE, stdin=PIPE, stderr=STDOUT)    
                p_out = p_command.communicate(b"n\n")[0]
                v_out = v_command.communicate(b"n\n")[0]
                print(p_out, v_out)

    writer.writeheader()
    writer.writerow(empty_dict)


# with open('reverie-tests-output.csv', mode='w') as csv_file:
#     fieldnames = ['num parties', 'soundness level', 'num repetitions', 'rows of matrix', 'columns of matrix', 'proof size', 'prover runtime', 'verifier runtime']
#     writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

#     empty_dict = {'num parties': 0, 'soundness level': 0, 'num repetitions': 0, 'rows of matrix': 0, 'columns of matrix': 0, 'proof size': 0, 'prover runtime': 0, 'verifier runtime': 0}


#     writer.writeheader()
#     writer.writerow(empty_dict)

