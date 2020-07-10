
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
input: /
output: (int, int)

hardcode randomness epsilon and r
will be replaced later by Fiat.Shamir.py
"""
def hardcodeER():
    e = Value()
    r = Value()
    e.getRand()
    r.getRand()
    return (e, r)

"""
    function independent section
"""

"""
input: /
output: Value

generate cryptographically secure randomness lambda
"""
def getLambda():
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
    # TODO: replace randomness with Fiat-Shamir
    (epsilon, r) = hardcodeER()
    ret = 0
    i = 0
    while i <= (len(triples)//2):
        (x, y, z) = triple[i]
        (a, b, c) = triple[i+1]
        # epsilon trick
        d = epsilon*x + a
        e = y + b
        v = epsilon * z + (d*e + d*b + e*a + c)
        # random linear combination trick
        ret += (r*v).value
        i += 2
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
    
