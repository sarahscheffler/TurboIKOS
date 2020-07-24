"""see slide 6. especially for the comment from sarah for an improvement"""


from Value import Value



# input: external file
# output:in array of dictionaries.
# function:: parse external file


def parse(argv, n_gate, gate):
    l = [None]*n_gate
    next(argv)
    i = 0
    for line in argv:
        n = line.strip('\n').split(' ')
        input1, input2, output, operation = int(
            n[2]), int(n[3]), int(n[4]), n[5]
        g = gate(input1, input2, output, operation=operation)
        l[i] = g
        i = i + 1
        if i == n_gate:
            break
    return l

    """
	index of array corresponds to topological order of circuit
    """



#input: array of circuit classs, wire object
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
def compute_e(circuit, wire):
    for i in range(n_gate):
        c = circuit[i]
        #calculate and set x_e
        x_v = sum(wire.v(c.x).value)
	x_lam = sum(wire.lambda_val(c.x).val)
        x_e = Value(x_v + x_lam)
	wire.set_e(c.x, x_e)
	#calculate and set y_v
        y_v = sum(wire.v(c.y).value)
        y_lam = sum(wire.lambda_val(c.y).val)
        y_e = Value(y_v + y_lam)
        wire.set_e(c.y, y_e)
    return 1
'''

'''

