
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
from Cryptodome.Util.number import bytes_to_long
import Value

"""
    temporary/helper functions
"""

"""
input: /
output: (bytes, bytes)

hardcode randomness epsilon and r
will be replaced later by Fiat.Shamir.py
"""
def hardcodeER():
    return (os.urandom(16), os.urandom(16))

"""
input: integer, integer
output: list of integers

split val into n random shares
"""
def splitData(val, n):
    ret = []
    for i in range(n-1):
        ret.append(random.randint(0,val))
    last = val - sum(ret)
    ret.append(last)
    return ret

"""
    function independent section
"""

"""
input: wire
output: bytes

generate cryptographically secure randomness lambda
"""
def getLambda():
    # if !wire:
        # wire.lambda = bytes_to_long(os.urandom(16))
    # return wire.lambda
    return Value.wrapLambda()

"""
input: list
output: boolean

take a list of triples and randomly partition them into pairs
call Fiat-Shamir.py to calculate each epsilon and r
calculate v
output whether the final random linear combination equals 0
"""
def randomLC(triples):
    # TODO: replace randomness with Fiat-Shamir
    (epsilon, r) = hardcodeER()
    epsilon = bytes_to_long(epsilon)
    r = bytes_to_long(r)
    ret = 0
    for i in range(len(triples)):
        (x, y, z) = genTriple(getLambda(), getLambda())
        (a, b, c) = triples[i]
        # epsilon trick
        d = epsilon*x + a
        e = y + b
        v = epsilon * z - (d*e - d*b - e*a + c)
        # random linear combination trick
        ret += r*v
    return (ret == 0)

"""
    function dependent section
"""

"""
input: integer, integer
output: integer

generate a Beaver's triple according to lambdas
"""
def genTriple(lamA, lamB):
    lamC = Value.wrapOperation(lamA, lamB)
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
def assignLambda(circuit, n):
    # for gate in circuit:
        # (TODO: wrapper on operation)
        # if gate == add:
            # getLambda(inputwire1)
            # getLambda(inputwire2)
            # outputwire.lambda = inputwire1.lambda + inputwire2.lambda
        # else if gate == mul:
            # getLambda(inputwire1)
            # getLambda(inputwire2)
            # triple = genTriple(inputwire1.lambda,inputwire2.lambda)
            # triples.append(triple)
            # outputwire.lambda = triple[2]
        # else:
            # try:
                # pass
            # except:
                # print("Unrecognized gate type")
    # for wire in circuit:
        # splitData(wire.lambda, n)
    # return (circuit, triples)
    pass
    
