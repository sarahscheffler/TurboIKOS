"""see slide 6. especially for the comment from sarah for an improvement"""

import sys
import gate
#import wire

#input: external file 
#output:in array of dictionaries. 
#function:: parse external file
def parse(argv, n_gate):
	l = [None]*n_gate
	next(argv)
	i = 0
	for line in argv:
		n = line.strip('\n').split(' ')	
		input1, input2, output, operation = int(n[2]), int(n[3]), int(n[4]), n[5]
		g = gate.gate(input1, input2, output, operation = operation)
		l[i] = g
		i = i + 1
		if i == n_gate:
			break
	return l	
	
	"""
	index of array corresponds to topological order of circuit
	"""

#input: array of circuit classs
#output: array of e broadcast 
#Write v shares and e to output value
def compute_output(circuit):
	broadcast = []
	for i in range(n_gate):
		c = circuit[i]
		if c.operation == 'MUL' or 'AND':
			broadcast.append(c.mul())
		if c.operation == 'MUL' or 'XOR':
			c.add()
	return broadcast
		

#input:array of circuit class
#output: NA
#Assign e values of input wires
def compute_e(circuit):
	for i in range(n_gate):
		c = circuit[i]
		#calculate lambdas and vs from shares
		lam_x = 0 
		lam_y = 0
		v_x = 0
		v_y = 0
		for j in range(n_parties):
			lam_x = lam_x + wire.acceess_wire(c.x, lambda, j)
			lam_y = lam_y + wire.acceess_wire(c.y, lambda, j) 
			v_x = v_x + wire.acceess_wire(c.x, v, j)
			v_y = v_y + wire.acceess_wire(c.y, v, j)
		wire.insert_wire(c.x, 'e', lam_x + v_x)
		wire.insert_wire(c.y, 'e', lam_y + v_y) 

def main():
	#Parse data 
	input_stream = sys.argv[1]
	with open(input_stream) as f:
		first_line = f.readline().split()
		global n_gate
		n_gate = int(first_line[0])
		global n_wire
		n_wire = int(first_line[1])
		second_line = f.readline().split()
		global n_input
		n_input = int(second_line[0])
		#create list of number of wires for input values
		global l_input
		l_input = [None]*n_input
		for i in range(n_input):
			l_input[i] = int(second_line[i+1])
		third_line = f.readline().split()
		global n_output
		n_output = int(third_line[0])
		#create list of number of wires for output values
		global l_output
		l_output = [None]*n_output
		for i in range(n_output):
			l_output[i]=int(third_line[i+1])
		#create list of gate
		global circuit
		circuit = parse(f, n_gate)	
	#Create list of wire data
	global n_parties	
	n_parties = 3
	global wire_data
	wire_data = [{'e' : None, 'v': []*n_parties, 'lambda': []*n_parties} for i in range(n_wire)]
if __name__ == '__main__':
     main()

