import sys
import Value as v


"""
input: external file
output: circuit data struct (array of gate objects in topological order
        list of # wires of input 
        list of # wires of output
        numbers of gates
        numbers of wires
        number of outputs
        nymber of inputs
function:: parse external file in Bristol format
"""
n_epsilons = 1
def parse_bristol(gate, n_parties, i):
    input_stream = sys.argv[i]
    n_mulgate = 0 
    n_addgate = 0
    n_scagate = 0
    n_inv = 0 
    with open(input_stream, 'r') as f:
        first_line = f.readline().split()
        n_gate = int(first_line[0])
        n_wires = int(first_line[1])
        second_line = f.readline().split()
        n_input = int(second_line[0])
        l_input = [1 for i in range(n_input)]

        mult_gates = []
    
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
            
            g = gate(input1, input2, output, n_parties, operation=operation)
            l[i] = g
            i = i + 1

            if operation == 'ADD' or operation == 'XOR':
                n_addgate += 1
            elif operation == 'MUL' or operation == 'AND':
                n_mulgate += 1
                mult_gates.append(g)
            elif operation == 'INV' or operation == 'NOT': 
                n_inv += 1
            elif operation == 'SCA':
                input2 = v.Value(input2, v.getfield())
                n_scagate += 1
            
            if i == n_gate:
                break
    c_info = {'l input': l_input, 'n_gate': n_gate, 'n_wires': n_wires, 'n_output': n_output, 'n_input': n_input, 'n_addgate': n_addgate, 'n_mul': n_mulgate, 'n_inv': n_inv, \
                'n_parties': n_parties, 'n_sca': n_scagate, 'mult_gates': mult_gates}
    return l, l_input, l_output, n_gate, n_wires, n_output, n_input, n_addgate, n_mulgate, n_parties, c_info, n_scagate

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
def parse_inputs():
    with open(sys.argv[2], 'r') as f:
        line = f.readline()
        inputs_l = (line.split(' '))
        inputs = []
        for i in inputs_l:
            if i != "\n":
                inputs.append(v.Value(int(i)))
        line = f.readline()
        outputs_l = (line.split(' '))
        outputs = []
        for i in outputs_l:
                if i != "":
                    outputs.append(v.Value(int(i)))
    return inputs, outputs
def parse_test(gate, n_parties, i):
    with open(sys.argv[i], 'r') as f:
        first_ch = f.readline()[0]
        if first_ch == 'P':
            return parse_pws(gate, n_parties, i)
        else:
            return parse_bristol(gate, n_parties, i)

"""
input: circuit object, epsilon1, epsilon2, wire data structure, number of gates, number of parties
output: array of array of alpha values. row# = mul gate#, col# = party# 
Write to output wires of each gate and compute alpha values.  
"""
def compute_output(circuit, wire, n_gate, n_parties):
    m = 0
    for i in range(n_gate):
        c = circuit[i]
        #MUL gates
        if c.operation == 'MUL' or c.operation == 'AND':
            c.w = wire
            c.mult(m)
            m += 1
        # ADD gates	
        if c.operation == 'ADD' or c.operation== 'XOR':
            c.w = wire
            c.add()
        if c.operation == 'INV' or c.operation == 'NOT': 
            c.w = wire
            c.inv()
        # Scalar mult gates (new code)
        if c.operation == 'SCA':
            c.w = wire
            c.sca()