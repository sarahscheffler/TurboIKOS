"""see slide 6. especially for the comment from sarah for an improvement"""

import sys
import gate
import wire

#input: external file 
#output:in array of dictionaries. 
#function:: parse external file
def parse(argv):
	first_line = argv.readline().split()
	n_gate = int(first_line[0])
	n_wire = int(first_line[1])
	l = [None]*n_gate
	next(argv)
	next(argv)
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
	input_stream = sys.argv[1]
	with open(input_stream) as f:
		l = parse(f)

if __name__ == '__main__':
     main()
