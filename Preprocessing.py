
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
from Value import Value
import Value as v
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from Cryptodome.Util.number import long_to_bytes, bytes_to_long
from gmpy2 import mpz

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
 
def getranbyte(num_bytes): #getRandomBytes : int -> bytes getRandomBytes(16) creates a 16-byte random number (not a Value)
    return bytes_to_long(os.urandom(num_bytes))

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
        elif gate.operation == 'INV' or gate.opeartion == 'NOT': 
            wire.set_lambda(gate.z, [None]*n_parties)
            if wire.lambda_val(gate.x) == None:
                x_lam = getRandom()
                wire.set_lambda(gate.x, x_lam.splitVal(n_parties))
            for i in range(n_parties):
                if i == 0:
                    wire.lambda_val(gate.z)[i] = wire.lambda_val(gate.x)[i] + Value(1) 
                else: 
                    wire.lambda_val(gate.z)[i] = wire.lambda_val(gate.x)[i]
        else:
            try:
                pass
            except:
                print("Unrecognized gate type")
    return 1
   
def generateNum(cipher, lambda_type, index):
    assert(lambda_type == 'lambda' or \
         lambda_type == 'lambda y hat' or \
              lambda_type == 'lambda z hat'), "Lambda type is invalid"
    number = cipher.encrypt(pad(lambda_type.encode() + str(index).encode(), AES.block_size))
    return Value(bytes_to_long(number))

def rebuildlambda(party, seed, circuit, c_info):
    n_input = c_info['n_input']
    n_ouput = c_info['n_output']
    c_nmul = c_info['n_mul']

    cipher = AES.new(long_to_bytes(seed), AES.MODE_ECB)
    n_mult = 0

    lambda_val = [None]*n_input
    lambda_z = []
    lam_y_hat = [None]*c_nmul
    lam_z_hat = [None]*c_nmul

    for gate in circuit:
        x = gate.x
        y = gate.y 
        z = gate.z
        if gate.operation == "ADD" or gate.operation == "XOR":
            #calculate lambdas from PR generateNum
            if x < n_input:
                x_lam = generateNum(cipher, 'lambda', x)
                lambda_val[x] = x_lam
            if y < n_input:
                y_lam = generateNum(cipher, 'lambda', y)
                lambda_val[y] = y_lam
            z_lam = x_lam + y_lam
            lam_z_hat.append(z_lam)
        elif gate.operation == "MUL" or gate.operation == "AND": 
            #calculate lambdas 
            if x < n_input:
                x_lam = generateNum(cipher, 'lambda', x)
                lambda_val[x] = x_lam
            if y < n_input:
                y_lam = generateNum(cipher, 'lambda', y)
                lambda_val[y] = y_lam
            
            #set y lam hat
            y_lam_hat = generateNum(cipher, 'lambda y hat', n_mult) 
            lam_y_hat[n_mult] = y_lam_hat
            #set z lam 
            z_lam = generateNum(cipher, 'lambda', z)  
            lambda_z.append(z_lam)
            #set z lam hat 
            z_lam_hat = generateNum(cipher, 'lambda z hat', n_mult)
            lam_z_hat[n_mult] = z_lam_hat
            n_mult += 1
    return lambda_val, lambda_z, lam_y_hat, lam_z_hat

def make_party_seeds(n_parties):
    party_master_seed_value = [getranbyte(16) for i in range(n_parties)] #array of int
    return party_master_seed_value

#pseudorandom assignment for lambdas 
def PRassignLambda(circuit, wire, n_parties):
    party_master_seed_value = make_party_seeds(n_parties)
    party_master_seed = [AES.new(long_to_bytes(i), AES.MODE_ECB) for i in party_master_seed_value] 
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
            gate.b = wire.lam_hat(gate.y)
            gate.c = wire.lam_hat(gate.z)
            triples.append([sum(wire.lambda_val(gate.x)), y_lam_hat, z_lam_hat])
            n_mult += 1
        else: 
            try: 
                pass
            except: 
                print("Unrecognized gate type")

    return triples, party_master_seed_value
