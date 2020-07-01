
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

import os

"""
    temporary/helper functions
"""

# input: /
# output: bytes
# hardcode randomness epsilon and r
# will be replaced later by Fiat.Shamir.py
def hardcodeER():
    pass

# input: integer, integer
# output: list of integers
# split val into n random shares
def splitData(val, n):
    pass

"""
    function independent section
"""

# input: /
# output: bytes
# generate cryptographically secure randomness lambda
def getLambda():
    pass

# input: list
# output: boolean
# take a list of triples and randomly partition them into pairs
# call Fiat-Shamir.py to calculate each epsilon and r
# calculate v
# output whether the final random linear combination equals 0
def randomLC(vs):
    pass

"""
    function dependent section
"""

# input: /
# output: tuple
# call getLambda() for lambdas
# generate a Beaver's triple according to lambdas
def genTriple():
    pass

# input: list, integer
# output: list
# take the list representing the circuit
# for input wires, call getLambda()
# for output wires of add gates, propagate
# for output wires of mul gates, call genTriple()
# call splitData() to split the shares into n parties
# output the circuit with lambdas updated for each wire
def assignLambda(circuit, n):
    pass


