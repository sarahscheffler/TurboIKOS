
"""
    Preprocessing.py
    - function independent section
      1. generate random lambdas
      2. sacrifice
      3. random linear combination
    - function dependent section
      1. assign lambdas to wires
      2. generate beaver triples
      3. split data for parties
"""

from Value import Value

"""
    temporary/helper functions
"""

"""
    function independent section
"""

"""
input: /
output: Value

generate cryptographically secure randomness lambda
"""
def getRandom():
    lam = Value()
    lam.getRand()
    return lam

"""
input: list
output: boolean

take a list of triples and randomly partition them into pairs
call Fiat-Shamir.py to calculate each epsilon and r
calculate v
output whether the final random linear combination equals 0
"""
def randomLC(triples):
    assert(len(triples)%2 == 0)
    # TODO: replace epsilon with Fiat-Shamir
    epsilon = getRandom()
    ret = 0
    i = 0
    while i <= (len(triples)//2):
        (x, y, z) = triples[i]
        (a, b, c) = triples[i+1]
        # epsilon trick
        d = epsilon*x - a
        e = y - b
        v = epsilon*z - (d*e + d*b + e*a + c)
        # random linear combination trick
        # TODO: replace r with Fiat-Shamir
        r = getRandom()
        ret += (r*v).value
        i += 2
    return (ret == 0)

"""
    function dependent section
"""

"""
input: Value, Value
output: tuple

generate a Beaver's triple according to lambdas
"""
def genTriple(lamA, lamB):
    lamC = lamA*lamB
    return (lamA, lamB, lamC)

"""
input: list, integer
output: list, list

take the list representing the circuit
for input wires, call getLambda()
for output wires of add gates, propagate
for output wires of mul gates, call genTriple()
call splitData() to split the shares into n parties
output the circuit with lambdas updated for each wire
"""
def assignLambda(circuit, wire_data, n):
    triples = []
    for gate in circuit:
        if gate.operation == "ADD" or gate.operation == "XOR":
            wire_data[gate.x]['lambda'].getRand()
            wire_data[gate.y]['lambda'].getRand() 
            wire_data[gate.z]['lambda'] = wire_data[gate.x]['lambda'] + \
                                          wire_data[gate.y]['lambda']
        elif gate.operation == "MUL" or gate.operation == "AND":
            wire_data[gate.x]['lambda'].getRand()
            wire_data[gate.y]['lambda'].getRand()
            wire_data[gate.z]['lambda'].getRand()
            gate.a = wire_data[gate.x]['lambda']
            gate.b = wire_data[gate.y]['lambda']
            gate.c = genTriple(gate.a, gate.b)[2]
            triples.append([gate.a, gate.b, gate.c])
            triples.append(genTriple(getRandom(), getRandom()))
        else:
            try:
                pass
            except:
                print("Unrecognized gate type")
    for wire in wire_data:
        wire['lambda'] = wire['lambda'].splitVal(n)
    return (circuit, wire_data, triples)

    
class gate:
	#input: 2 inputs, 3 triples/ 0's
	def __init__(self, input1, input2, output,*, triple1 = Value(), triple2 = Value(), triple3 = Value(), operation = None):	
		self.x = input1
		self.y = input2
		self.z = output
		if operation == 'AND' or 'MUL':
			self.a = triple1
			self.b = triple2
			self.c = triple3
		if operation == 'XOR' or 'ADD':
			self.a = None
			self.b = None
			self.c = None
		self.operation = operation
