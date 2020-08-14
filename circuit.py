"""see slide 6. especially for the comment from sarah for an improvement"""

import sys
from Value import Value



# input: external file
# output: circuit data struct (array of gate objects in topological order
#         list of # wires of input 
#         list of # wires of output
#         numbers of gates
#         numbers of wires
#         number of outputs
#         nymber of inputs
# function:: parse external file


def parse(gate):
    input_stream = sys.argv[1]
    with open(input_stream) as f:
        first_line = f.readline().split()
        n_gate = int(first_line[0])
        n_wires = int(first_line[1])
        second_line = f.readline().split()
        n_input = int(second_line[0])
        # create list of number of wires for input value
        l_input = [None]*n_input
        for i in range(n_input):
            l_input[i] = int(second_line[i+1])
        third_line = f.readline().split()
        n_output = int(third_line[0])
        # create list of number of wires for output values
        l_output = [None]*n_output
        for i in range(n_output):
            l_output[i] = int(third_line[i+1])
        l = [None]*n_gate
        next(f)
        i = 0
        for line in f:
            n = line.strip('\n').split(' ')
            input1, input2, output, operation = int(
            n[2]), int(n[3]), int(n[4]), n[5]
            g = gate(input1, input2, output, operation=operation)
            l[i] = g
            i = i + 1
            if i == n_gate:
                break
    return l, l_input, l_output, n_gate, n_wires, n_output, n_input

    """
	index of array corresponds to topological order of circuit
    """
# input: number of wires
# output: wire data structure (array of dictionaries with keys 'e', 'v', 'lambda, 'lam_hat', 'e_hat' with index of wire#

def wire_data(n_wires):
    return [{'e': None, 'v': Value() , 'lambda': None, 'lam_hat':Value(), 'e_hat': None}
                 for i in range(n_wires)]

#input: circuit object, epsilon1, epsilon2, wire data structure, number of gates, number of parties
#output: array of array of alpha values. row# = mul gate#, col# = party# 
#Write to output wires of each gate and compute alpha values.  
def compute_output(circuit, epsilon_1, epsilon_2, wire, n_gate, n_parties):
    alpha_broadcast = []
    for i in range(n_gate):
        c = circuit[i]
        #MUL gates
        if c.operation == 'MUL' or c.operation == 'AND':
            c.w = wire
            c.mult()
	    # calculate alpha share
            alpha_shares = [None]*n_parties
            for j in range(n_parties):
                y_lam = wire.lambda_val(c.y)[j]
                y_lamh = wire.lam_hat(c.y)[j]
                alpha_shares[j] = epsilon_1[i]*y_lam + (epsilon_2[i]*y_lamh)
            alpha_broadcast.append(alpha_shares)
        # ADD gates	
        if c.operation == 'ADD' or c.operation== 'XOR':
            c.w = wire
            c.add() 
    return alpha_broadcast

#input: circuit, wire structure, list of n_mul gate alphas, and two epsilons
#output: n_parties zeta shares
def compute_zeta_share(circuit, wire, alpha, epsilon_1, epsilon_2, n_parties):
    r = [None]*n_parties
    
    for i in range(n_parties):
        zeta = 0
        n = 0
        for j in range(len(circuit)):
            if circuit[j].operation == 'AND' or  circuit[j].operation == 'MUL':
                x = circuit[j].x
                y = circuit[j].y
                z = circuit[j].z
                A = sum(alpha[n])
                zeta += (epsilon_1[j] * wire.e(y) - A)* wire.lambda_val(x)[i] + \
                    epsilon_1[j] * wire.e(x) * wire.lambda_val(y)[i] - \
                    epsilon_1[j] * wire.lambda_val(z)[i] - epsilon_2[j] * wire.lam_hat(z)[i]     
                n += 1
                if i == 0:
                    zeta += epsilon_1[j] * wire.e(z) - epsilon_1[j]*wire.e(x)*wire.e(y) + epsilon_2[j]*wire.e_hat(z)
        r[i] = (zeta)
    return r 
