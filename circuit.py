"""see slide 6. especially for the comment from sarah for an improvement"""

import sys
#import gate
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
		d = dict(inputs = [input1, input2], output = output, operation = operation)
		l[i] = d
		i = i + 1
		if i == n_gate:
			break
	return l	
	
	"""
	index of array corresponds to topological order of circuit                                                              dict: {inputwires, outputwire, operation}
	"""

#input: array of dictionaries and wire
#output: array of internal outputs
#compute real values of output wires and store values on wires
def compute_real(array, wire):
	pass

#input:array of dictionaries and wire
#output: array of dictionaries of public values e
#compute public broadcast e = v + lambda and store e on wires
def compute_public(array, wire):
	pass

def main():
	#Parse data 
	input_stream = sys.argv[1]
	with open(input_stream) as f:
		first_line = f.readline().split()
		n_gate = int(first_line[0])
		n_wire = int(first_line[1])
		second_line = f.readline().split()
		n_input = int(second_line[0])
		#create list of number of wires for input values
		l_input = [None]*n_input
		for i in range(n_input):
			l_input[i] = int(second_line[i+1])
		third_line = f.readline().split()
		n_output = int(third_line[0])
		#create list of number of wires for output values
		l_output = [None]*n_output
		for i in range(n_output):
			l_output[i]=int(third_line[i+1])
		#create list of gate
		circuit = parse(f, n_gate)	
		

if __name__ == '__main__':
     main()

