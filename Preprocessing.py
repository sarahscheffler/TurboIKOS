
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
import random

"""
    temporary/helper functions
"""

# input: /
# output: (bytes, bytes)
# hardcode randomness epsilon and r
# will be replaced later by Fiat.Shamir.py
def hardcodeER():
    return (os.urandom(16), os.urandom(16))

# input: integer, integer
# output: list of integers
# split val into n random shares
def splitData(val, n):
    ret = []
    for i in range(n-1):
        ret.append(random.randint(val))
    last = val - sum(ret)
    ret.append(last)
    return ret

"""
    function independent section
"""

# input: /
# output: bytes
# generate cryptographically secure randomness lambda
def getLambda():
    return os.urandom(16)

# input: list
# output: boolean
# take a list of triples and randomly partition them into pairs
# call Fiat-Shamir.py to calculate each epsilon and r
# calculate v
# output whether the final random linear combination equals 0
def randomLC(vs):
    assert(len(vs)%2 == 0)
    # TODO: replace randomness with Fiat-Shamir
    (epsilon, r) = hardcodeER()
    ret = False
    # group triples into pairs
    for (verified, sacrificed) in paired:
        # epsilon trick
    # random linear combination trick
    return ret

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

