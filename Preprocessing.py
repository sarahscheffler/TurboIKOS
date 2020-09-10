
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


#inputs: circuit, wire object, number of parties
#output: list of triples
#function: assign lambda x, lambda y, lambda z for add gates 
#assign lambda hat y, lambda hat z, lambda z for mul gates
#assign triple shares to gate
def assignLambda(circuit, wire, n_parties):
    triples = []
    for gate in circuit:
        if gate.operation == "ADD" or gate.operation == "XOR":
            if wire.lambda_val(gate.x) == None:
                x_lam = getRandom()
                wire.set_lambda(gate.x, x_lam.splitVal(n_parties))
            if wire.lambda_val(gate.y) == None:
                y_lam = getRandom()
                wire.set_lambda(gate.y, y_lam.splitVal(n_parties))
            z_lam_share = []
            for i in range(n_parties):
                z_lam_share.append(wire.lambda_val(gate.x)[i] + \
                                   wire.lambda_val(gate.y)[i])
            wire.set_lambda(gate.z, z_lam_share)
        elif gate.operation == "MUL" or gate.operation == "AND":
            #set x_lam and y_lam if they are not set
            if wire.lambda_val(gate.x) == None:
                x_lam = getRandom()
                wire.set_lambda(gate.x, x_lam.splitVal(n_parties))
            if wire.lambda_val(gate.y) == None:
                y_lam = getRandom()
                wire.set_lambda(gate.y, y_lam.splitVal(n_parties))
            
            #set y_lam_hat
            y_lam_hat = getRandom()
            wire.set_lam_hat(gate.y, y_lam_hat.splitVal(n_parties))
            #set z_lam
            z_lam = getRandom()
            wire.set_lambda(gate.z, z_lam.splitVal(n_parties))
            #set z_lam_hat
            z_lam_hat = getRandom()
            wire.set_lam_hat(gate.z, z_lam_hat.splitVal(n_parties))
                       
        else:
            try:
                pass
            except:
                print("Unrecognized gate type")
    return 1
