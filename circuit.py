"""see slide 6. especially for the comment from sarah for an improvement"""

import sys
from Value import Value



# input: external file
# output:in array of dictionaries.
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

def wire_data(n_wires):
    return [{'e': None, 'v': Value() , 'lambda': Value(), 'lam_hat':Value(), 'e_hat': None}
                 for i in range(n_wires)]

#output: array of e broadcast 
#Write v shares and e to output value
def compute_output(circuit, epsilon_1, epsilon_2, wire):
    alpha_broadcast = []
    for i in range(n_gate):
        c = circuit[i]
        if c.operation == 'MUL' or c.operaton == 'AND':
            c.mul()
	    # calculate alpha share
            alpha_shares = []*n_parties
            for i in range(n_parties):
                y_lam = wire.lambda_val(self.y)[i]
                y_lamh = wire.lambda_hat(self.y)[i]
                alpha_shares[i] = epsilon_1[i]*y_lam + (epsilon_2[i]*y_lamh)
            alpha_broadcast.append(alpha_shares)	
        if c.operation == 'ADD' or c.operation== 'XOR':
            c.add()
    return alpha_broadcast

#input:array of circuit class, wire object
#output: NA
#Assign e values of input wires
def compute_e(circuit, wire, n_gate):
    for i in range(n_gate):
        c = circuit[i]
        #calculate and set x_e
        x_v = sum(wire.v(c.x))
        print('lambda:', wire.lambda_val(c.x))
        x_lam = sum(wire.lambda_val(c.x))
        x_e = (x_v + x_lam)
        wire.set_e(c.x, x_e)
	#calculate and set y_v
        y_v = sum(wire.v(c.y))
        y_lam = sum(wire.lambda_val(c.y))
        y_e = (y_v + y_lam)
        wire.set_e(c.y, y_e)
    return 1

#input: circuit, wire structure, list of n_mul gate alphas, and two epsilons
#output: n_parties zeta shares
def compute_zeta_share(circuit, wire, alpha, epsilon_1, epsilon_2, n_parties):
    r = []*n_parties
    
    for i in range(n_parties):
        zeta = 0
        n = 0
        for j in range(len(circuit)):
            if circuit[j].operation == 'AND' or 'MUL':
                x = circuit[j].x
                y = circuit[j].y
                z = circuit[j].z
                A = alpha[i][n]
                s = (epsilon_1 * wire.e(y) - A)* wire.lambda_val(x)[j] + \
                    epsilon_1 * wire.e(x) * wire.lambda_val(y)[j] - \
                    epsilon_2 * wire.e(z) - epsilon_2 * wire.lam_hat(z)     
                n += 1
            if i == 0:
                s += epsilon_1 * wire.e(z) - epsilon_1*wire.e(x)*wire.e(y) + epsilon_2*wire.e_hat(z)
        zeta += s
    r.append(zeta)
    return r 
