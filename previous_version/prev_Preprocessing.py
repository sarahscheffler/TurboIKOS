
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
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.number import long_to_bytes

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

def assignLambda_old(circuit, wire_data, n):
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
"""

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
            #set triples
            gate.a = wire.lambda_val(gate.x)
            gate.b = wire.lam_hat(gate.y)
            gate.c = wire.lam_hat(gate.z) 
            triples.append([sum(wire.lambda_val(gate.x)),y_lam_hat, z_lam_hat])
                       
        else:
            try:
                pass
            except:
                print("Unrecognized gate type")
    return triples
   
def generateNum(seed, lambda_type, index):
    cipher = AES.new(seed, AES.MODE_ECB)
    assert(lambda_type == 'lambda' or lambda_type == 'lambda y hat' or lambda_type == 'lambda z hat'), "Lambda type is invalid"
    number = cipher.encrypt(pad(lambda_type + str(index), AES.block_size))
    return Value(number)

def rebuildlambda(party, seed, circuit, wire, n_parties):
    cipher = AES.new(seed, AES.MODE_ECB)
    none_arr = [None*n_parties]
    n_mult = 0
    for gate in circuit:
        if gate.operation == "ADD" or gate.operation == "XOR":
            #set lambda_val of gate to none_arr 
            if wire.lambda_val(gate.x) == None:
                wire.set_lambda(gate.x, none_arr) 
            if wire.lambda_val(gate.y) == None:
                wire.set_lambda(gate.y, none_arr)
            if wire.lambda_val(gate.z) == None:
                wire.set_lambda(gate.z, none_arr)

            #calculate lambdas from PR generateNum
            if wire.lambda_val(gate.x)[party] == None:
                x_lam = generateNum(seed, 'lambda', gate.x)
                wire.lambda_val(gate.x)[party] = x_lam
            if wire.lambda_val(gate.y)[party] == None:
                y_lam = generateNum(seed, 'lambda', gate.y)
                wire.lambda_val(gate.y)[party] = y_lam
            z_lam = x_lam + y_lam
            wire.lambda_val(gate.z)[party] = z_lam
        elif gate.operation == "MUL" or gate.operation == "AND": 
            if wire.lambda_val(gate.x) == None:
                wire.set_lambda(gate.x, none_arr) 
            if wire.lambda_val(gate.y) == None:
                wire.set_lambda(gate.y, none_arr)
            
            #calculate lambdas 
            if wire.lambda_val(gate.x) == None:
                x_lam = generateNum(seed, 'lambda', gate.x)
                wire.lambda_val(gate.x)[party] = x_lam
            if wire.lambda_val(gate.y) == None:
                y_lam = generateNum(seed, 'lambda', gate.y)
                wire.lambda_val(gate.y)[party] = y_lam
            
            #set y lam hat
            y_lam_hat = generateNum(seed, 'lambda y hat', n_mult) 
            wire.lam_hat(gate.y)[party] = y_lam_hat
            #set z lam 
            z_lam = generateNum(seed, 'lambda', gate.z)
            wire.lambda_val(gate.z, z_lam)
    return wire

#pseudorandom assignment for lambdas 
def PRassignLambda(circuit, wire, n_parties):
    party_master_seed_value = [getRandom() for i in range(n_parties)]
    party_master_seed = [(long_to_bytes(i.value)) for i in party_master_seed_value] 
    triples = []
    n_mult = 0
    for gate in circuit:
        if gate.operation == "ADD" or gate.operation == "XOR":
            if wire.lambda_val(gate.x) == None:
                x_lambda = [generateNum(i, 'lambda', gate.x) for i in party_master_seed]
                wire.set_lambda(gate.x, x_lambda)
            if wire.lambda_val(gate.y) == None:
                y_lambda = [generateNum(i, 'lambda', gate.y) for i in party_master_seed]
                wire.set_lambda(gate.y, y_lambda)
            z_lam_share = []
            for i in range(n_parties):
                z_lam_share.append(wire.lambda_val(gate.x)[i] + wire.lambda_val(gate.y)[i])
            wire.set_lambda(gate.z, z_lam_share)
        elif gate.operation == "MUL" or gate.operation == "AND":
            if wire.lambda_val(gate.x) == None:
                x_lambda = [generateNum(i, 'lambda', gate.x) for i in party_master_seed]
                wire.set_lambda(gate.x, x_lambda)
            if wire.lambda_val(gate.y) == None:
                y_lambda = [generateNum(i, 'lambda', gate.y) for i in party_master_seed]
                wire.set_lambda(gate.y, y_lambda)
            
            #set y lam hate
            y_lam_hat = [generateNum(i, 'lambda y hat', n_mult) for i in party_master_seed]
            wire.set_lam_hat(gate.y, y_lam_hat)
            #set z lam 
            z_lam = [generateNum(i, 'lambda', gate.z) for i in party_master_seed]
            wire.set_lambda(gate.z, z_lam)
            #set z_lam_hat
            z_lam_hat = [generateNum(i, 'lambda z hat', n_mult) for i in party_master_seed]
            wire.set_lam_hat(gate.z, z_lam_hat)
            #set triples 
            gate.a = wire.lambda_val(gate.x)
            gate.b - wire.lam_hat(gate.y)
            gate.c = wire.lam_hat(gate.z)
            triples.append([sum(wire.lambda_val(gate.x)), y_lam_hat, z_lam_hat])
        else: 
            try: 
                pass
            except: 
                print("Unrecognized gate type")

    return triples, party_master_seed