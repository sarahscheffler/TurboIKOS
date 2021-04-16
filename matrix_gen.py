#!/usr/bin/env python3
import sys
import getopt
import numpy as np
import Value as v

#input: n, m
#output: random A, s, t
def gen_matrix(n, m):
    A = np.zeros((n, m), dtype=object)
    s = np.zeros((m, 1), dtype=object)
    
    for i in range(m):
        s[i][0] = v.Value()
        s[i][0].getBinRand()
    
    for i in range(n):
        for j in range(m):
            A[i][j] = v.Value()
            A[i][j].getRand()
    
    t = A.dot(s)
    return A, s, t


#input: n, m, file, matrix A
#write bristol format circuit to file f
def gen_circuit(n, m, f, A):
    #write header
    num_inputs = m
    num_outputs = n+m
    num_gates = n*(2*m-1) + m*3
    num_wires = m+ n*(2*(m-1)+1) + 3*m
    f.write("%d %d \n" % (num_gates, num_wires))
    f.write("%d " % num_inputs)
    f.write("1 "*num_inputs + "\n" )
    f.write("%d " % num_outputs)
    f.write("1 "*num_outputs + "\n" )
    
    #write gates
    input_w = 0
    internal_w = num_inputs
    output_w = num_wires - num_outputs + 1
    input_1 = num_inputs
    input_2 = num_inputs + 1
    for i in range(n):
        for j in range(m):
            f.write("2 1 %d %d %d SCA\n" % (input_w, A[i][j].value, internal_w))
            input_w += 1
            internal_w += 1
        
        input_w = 0
        
        for i in range(m-1):
            if i == m-2:
                f.write("2 1 %d %d %d XOR\n" % (input_1, input_2, output_w))
                output_w += 1
                input_1 += 1
                input_2 = input_1 + 1
            else:
                f.write("2 1 %d %d %d XOR\n" % (input_1, input_2, internal_w))
                input_1 = internal_w
                input_2 += 1
                internal_w += 1
    
    for i in range(m):
        f.write("2 1 %d %d %d AND\n" % (i, i, internal_w))
        internal_w += 1
        f.write("2 1 %d %d %d SCA\n" % (i, -1, internal_w))
        f.write("2 1 %d %d %d XOR\n" % (internal_w-1, internal_w, output_w))
        internal_w += 1
        output_w += 1



if __name__ == "__main__":

    opts, args = getopt.getopt(sys.argv[1:], "", ["row=", "col="])
    n = 0
    m = 0
    for o, a in opts:
        if o in ("--row"):
            n = int(a)
        elif o in ("--col"):
            m = int(a)
    A, s, t = gen_matrix(n,m)
    with open("circuits/matmult_%dx%d.txt" % (n,m), 'w') as f:
        gen_circuit(n, m, f, A)
