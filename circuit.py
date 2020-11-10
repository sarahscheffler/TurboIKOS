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
# function:: parse external file in Bristol format

n_epsilons = 1
def parse_bristol(gate, n_parties, i):
    input_stream = sys.argv[i]
    n_mulgate = 0 
    n_addgate = 0
    n_inv = 0 
    with open(input_stream, 'r') as f:
        first_line = f.readline().split()
        n_gate = int(first_line[0])
        n_wires = int(first_line[1])
        second_line = f.readline().split()
        # n_input = int(second_line[0])
        n_input = int(second_line[1]) + int(second_line[2])
        # create list of number of wires for input value
        # l_input = [int(second_line[i+1]) for i in range(n_input)]
        l_input = [1 for i in range(n_input)]
    
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
            if int(n[0]) == 2:
                input1, input2, output, operation = int(n[2]), int(n[3]), int(n[4]), n[5]
            elif int(n[0]) == 1: 
                input1, input2, output, operation = int(n[2]), None, int(n[3]), n[4]
            if operation == 'ADD' or operation == 'XOR':
                n_addgate += 1
            elif operation == 'MUL' or operation == 'AND':
                n_mulgate += 1
            elif operation == 'INV' or operation == 'NOT': 
                n_inv += 1
            g = gate(input1, input2, output, n_parties, operation=operation)
            l[i] = g
            i = i + 1
            if i == n_gate:
                break
    c_info = {'l': l, 'l input': l_input, 'n_gate': n_gate, 'n_wires': n_wires, 'n_output': n_output, 'n_input': n_input, 'n_addgate': n_addgate, 'n_mul': n_mulgate, 'n_inv': n_inv, 'n_parties': n_parties}
    return l, l_input, l_output, n_gate, n_wires, n_output, n_input, n_addgate, n_mulgate, n_parties, c_info

    """
	index of array corresponds to topological order of circuit
    """

def parse_pws(gate, n_parties, i):
    input_stream = sys.argv[i]
    n_mulgate = 0
    n_addgate = 0
    n_input = 0
    n_output = 0
    n_gate = 0
    n_wires = 0
    l_input = []
    l_output = []
    c = []
    with open(input_stream, 'r') as f:
        for line in f:
            l = line.strip('\n').split(' ')
            if l[0] == 'P':
                if l[3][0] == 'I':
                    n_wires += 1
                    n_input += 1
                    l_input.append(int(l[3][1:]))
                elif l[1][0] == 'O':
                    n_output += 1
                    l_output.append(int(l[1][1:]))
                else:
                    n_wires += 1
                    n_gate += 1
                    input1, input2, output = int(l[3][1:]), int(l[5][1:]), int(l[1][1:])
                    if l[4] == '*':
                        n_mulgate += 1
                        operation = 'MUL'
                    elif l[4] == '+':
                        n_addgate += 1
                        operation = 'ADD'
                    c.append(gate(input1, input2, output, n_parties, operation = operation))
    c_info = {'l input': l_input, 'n_gate': n_gate, 'n_wires': n_wires, 'n_output': n_output, 'n_input': n_input, 'n_addgate': n_addgate, 'n_mul': n_mulgate, 'n_parties': n_parties}
    return c, l_input, l_output, n_gate, n_wires, n_output, n_input, n_addgate, n_mulgate, n_parties, c_info

def parse(gate, n_parties):
    with open(sys.argv[1], 'r') as f:
        first_ch = f.readline()[0]
        if first_ch == 'P':
            return parse_pws(gate, n_parties, 1)
        else:
            return parse_bristol(gate, n_parties, 1)

def parse_test(gate, n_parties, i):
    with open(sys.argv[i], 'r') as f:
        first_ch = f.readline()[0]
        if first_ch == 'P':
            return parse_pws(gate, n_parties, i)
        else:
            return parse_bristol(gate, n_parties, i)

# input: number of wires
# output: wire data structure (array of dictionaries with keys 'e', 'v', 'lambda, 'lam_hat', 'e_hat' with index of wire#

def wire_data(n_wires):
    return [{'e': None, 'v': Value() , 'lambda': None, 'lam_hat': {} , 'e_hat': None}
                 for i in range(n_wires)]

#input: circuit object, epsilon1, epsilon2, wire data structure, number of gates, number of parties
#output: array of array of alpha values. row# = mul gate#, col# = party# 
#Write to output wires of each gate and compute alpha values.  
def compute_output(circuit, epsilon_1, epsilon_2, wire, n_gate, n_parties):
    alpha_shares_mulgate = []
    m = 0
    for i in range(n_gate):
        c = circuit[i]
        #MUL gates
        if c.operation == 'MUL' or c.operation == 'AND':
            c.w = wire
            c.mult(m)
	    # calculate alpha share
            alpha_shares = [None for x in range(n_parties)]
            for j in range(n_parties):
                y_lam = wire.lambda_val(c.y)[j]
                y_lamh = wire.lam_hat(c.y)[str(m)][j]
                # epsilon_1[e][m], y_lam, epsilon_2[e][m], y_lamh
                alpha_shares[j] = epsilon_1[m]*y_lam + (epsilon_2[m]*y_lamh)
            alpha_shares_mulgate.append(alpha_shares) #alpha[gate][epsilon][party]
            m += 1
        # ADD gates	
        if c.operation == 'ADD' or c.operation== 'XOR':
            c.w = wire
            c.add()
        if c.operation == 'INV' or c.operation == 'NOT': 
            c.w = wire
            c.inv()
    #compute single alpha for each mulgate (alpha = epsilon1*lambda_y + epsilon2*lambda_y_hat)
    alpha_broadcast = [None for x in range(len(alpha_shares_mulgate))] #alpha_broadcast[#mul_gate][#epsilon]
    for i in range(len(alpha_shares_mulgate)):
        alpha_broadcast[i] = sum(alpha_shares_mulgate[i])

    return alpha_broadcast, alpha_shares_mulgate

#input: circuit, wire structure, list of n_mul gate alphas, and two epsilons
#output: n_parties zeta shares
def compute_zeta_share(circuit, wire, alpha, epsilon_1, epsilon_2, n_parties):
    r = [None for x in range(n_parties)]
    for i in range(n_parties):
        zeta = 0
        n = 0
        for j in range(len(circuit)):
            if circuit[j].operation == 'AND' or  circuit[j].operation == 'MUL':
                x = circuit[j].x
                y = circuit[j].y
                z = circuit[j].z
                A = sum(alpha[n])
                #epsilon_1[e][n], wire.e(y), A, wire.lambda_val(x)[i], epsilon_1[e][n], wire.e(x), wire.lambda_val(y)[i], epsilon_1[e][n], wire.lambda_val(z)[i], epsilon_2[e][n], wire.lam_hat(z)[str(n)][i] 
                zeta += (epsilon_1[n] * wire.e(y) - A)* wire.lambda_val(x)[i] + \
                    epsilon_1[n] * wire.e(x) * wire.lambda_val(y)[i] - \
                    epsilon_1[n] * wire.lambda_val(z)[i] - epsilon_2[n] * wire.lam_hat(z)[str(n)][i]     
                
                if i == 0:
                    # epsilon_1[e][n], wire.e(z), epsilon_1[e][n], wire.e(x), wire.e(y), epsilon_2[e][n], wire.e_hat(z)
                    zeta += epsilon_1[n] * wire.e(z) - epsilon_1[n]*wire.e(x)*wire.e(y) + epsilon_2[n]*wire.e_hat(z)
                n+= 1   
        if j== len(circuit)-1:
            r[i] = (zeta)
    return r

#input: alpha_broadcast, alpha shares per mulgate, random values[#mulgate][#epsilon], number of parties, number of epsilons
#output: A shares[#party][epsilon]
def compute_A_share(alpha_broadcast, alpha_shares_mulgate, rand, n_parties):
    A = [None for x in range(n_parties)]
    for j in range(n_parties):
        cum = 0
        for m in range(len(alpha_broadcast)):
            cum += (rand[m]*alpha_shares_mulgate[m][j])
            if j == 0:
                cum -= (rand[m]*alpha_broadcast[m])
        A[j][e] = cum
    return A
                
