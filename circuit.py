"""see slide 6. especially for the comment from sarah for an improvement"""

import gate.py
import wire.py

#input: external file 
#output:in array of dictionaries. 
#function:: parse external file
def parse(argv):
	pass
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
