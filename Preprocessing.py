import os
from Value import Value
import Value as v
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from Cryptodome.Util.number import long_to_bytes, bytes_to_long
from gmpy2 import mpz, sub

import tree

"""
inputs: num_bytes: (int) number of bytes 
return: length num_bytes random byte string 
function: used to generate seeds for keys used for pseudorandom lambda generation 
""" 
def getranbyte(num_bytes): 
    x = (os.urandom(num_bytes))
    return x

"""
    function dependent section
"""
   
"""
input: 
    cipher: AES cipher 
    lambda_type: str, must be 'lambda', 'lambda y hat', or 'lambda z hat' 
    index: int, gate number 
output: 
    Value object of a byte string converted to a long 
function: 
    creates a pseudorandom value to be assigned to a lambda value, which verifier can use to rebuild 
"""
def generateNum(cipher, num_type, index):
    assert(num_type == 'lambda' or \
         num_type == 'lambda y hat' or \
              num_type == 'lambda z hat' or \
                  num_type == 'index' or \
                      num_type == 'random'), "Type input is invalid"
    
    if num_type == 'lambda': 
        num_type = 'l'
    elif num_type == 'lambda y hat':
        num_type = 'y'
    elif num_type == 'lambda z hat': 
        num_type = 'z'
    elif num_type == 'index':
        num_type = 'i'
    elif num_type == 'random':
        num_type = 'r'

    field = v.getfield()
    bits = round(v.get_bits())
    max_16 = (8**bits) 
    if field > max_16: 
        reject_val = (field//max_16)*max_16 
    else: 
        reject_val = (max_16//field)*field
    
    attempt = 0 
    number = bytes_to_long(cipher.encrypt(pad((num_type + str(index) + str(attempt)).encode(), AES.block_size))) 
    while number >= reject_val:
        attempt += 1
        number = bytes_to_long(cipher.encrypt(pad((num_type + str(index) + str(attempt)).encode(), AES.block_size))) 
    return Value(number%field)

"""
input: int, number of parties 
output: list, list of byte strings length of n_parties 
functino: generates a list of random strings to be used for PRlambda generation
"""
def make_party_seeds(n_parties):
    party_master_seed_value = [(getranbyte(16)) for i in range(n_parties)] 
    # (seeds, root) = tree.make_tree(n_parties)
    return party_master_seed_value

"""
input: 
    circuit: circuit object
    wire: wire object
    n_parties: int, number of parties 
output: 
    triples: list of triples 
    party_master_seed_value: list, list of byte strings 
function: 
    assign pseudorandom lambdas for prover 
    NOTE: verifier cannot use this function, verifier must use rebuildlambda
"""
def PRassignLambda(circuit, wire, n_parties, seeds):
    party_master_seed_value = seeds
    party_master_seed = [AES.new(i, AES.MODE_ECB) for i in party_master_seed_value] 

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
            
            #set y lam hat
            if str(n_mult) not in wire.lam_hat(gate.y): 
                y_lam_hat = [generateNum(i, 'lambda y hat', n_mult) for i in party_master_seed]
                wire.set_lam_hat(gate.y, y_lam_hat, n_mult)
            #set z lam 
            z_lam = [generateNum(i, 'lambda', gate.z) for i in party_master_seed]
            wire.set_lambda(gate.z, z_lam)
            #set z_lam_hat
            if str(n_mult) not in wire.lam_hat(gate.z):
                z_lam_hat = [generateNum(i, 'lambda z hat', n_mult) for i in party_master_seed]
                wire.set_lam_hat(gate.z, z_lam_hat, n_mult)
            #set triples 
            gate.a = wire.lambda_val(gate.x)
            gate.b = wire.lam_hat(gate.y)
            gate.c = wire.lam_hat(gate.z)
            triples.append([sum(wire.lambda_val(gate.x)), y_lam_hat, z_lam_hat])
            n_mult += 1
        elif gate.operation == "INV" or gate.operation == "NOT":
            #set initial lambda values as the same values from gate[x]
            if wire.lambda_val(gate.x) == None: 
                x_lambda = [generateNum(i, 'lambda', gate.x) for i in party_master_seed]
                wire.set_lambda(gate.x, x_lambda)
            wire.set_lambda(gate.z, [None]*n_parties)
            for i in range(n_parties): 
                if i == 0: 
                    wire.lambda_val(gate.z)[i] = (wire.lambda_val(gate.x)[i] + Value(1))
                else: 
                    wire.lambda_val(gate.z)[i] = (wire.lambda_val(gate.x)[i])
        #(new code)
        elif gate.operation == 'SCA':
            if wire.lambda_val(gate.x) == None:
                x_lambda = [generateNum(i, 'lambda', gate.x) for i in party_master_seed]
                wire.set_lambda(gate.x, x_lambda)
            z_lam_share = []
            for i in range(n_parties):
                z_lam_share.append(wire.lambda_val(gate.x)[i] *gate.y)
            wire.set_lambda(gate.z, z_lam_share)

        else: 
            try: 
                pass
            except: 
                print("Unrecognized gate type")

        # print("gate:", gate)
        # print("x:", wire.lambda_val(gate.x))
        # print("y:", wire.lambda_val(gate.y))
        # print("z:", wire.lambda_val(gate.z))

    return triples, party_master_seed_value

"""
input: 
    party: int, number association with party 
    seed: byte string of used for party's pseudorandom lambdas 
    circuit: circuit object
    c_info: dictionary, contains information about the circuit
output: 
    lambda_val: list, lambda vals in order of input gate
    lambda_z: list, lambda vals in order of output gates
    lam_y_hat: list, lam_y_hats 
    lam_z_hat: list, lam_z_hats
function: 
    for verifier to rebuild the lambda vals in format that verifier can digest 
"""
def rebuildlambda(party, seed, circuit, wire, c_info):
    n_input = c_info['n_input']
    n_ouput = c_info['n_output']
    c_nmul = c_info['n_mul']

    cipher = AES.new((seed), AES.MODE_ECB)
    n_mult = 0

    lambda_val = [Value(None)]*n_input
    lambda_z = []
    lam_y_hat = {}
    lam_z_hat = {}

    for gate in circuit:
        x = gate.x
        y = gate.y 
        z = gate.z
        if gate.operation == "ADD" or gate.operation == "XOR":
            #calculate lambdas from PR generateNum
            if x < n_input and lambda_val[x] == Value(None):
                x_lam = generateNum(cipher, 'lambda', x)
                wire.set_lambda(x, [x_lam])
            if y < n_input and lambda_val[y] == Value(None):
                y_lam = generateNum(cipher, 'lambda', y)
                wire.set_lambda(y, [y_lam])
            wire.set_lambda(z, [wire.lambda_val(x)[0] + wire.lambda_val(y)[0]])
        elif gate.operation == "MUL" or gate.operation == "AND": 
            #calculate lambdas 
            if x < n_input and lambda_val[x] == Value(None):
                x_lam = generateNum(cipher, 'lambda', x)
                wire.set_lambda(gate.x, [x_lam])
            if y < n_input and lambda_val[y] == Value(None):
                y_lam = generateNum(cipher, 'lambda', y)
                wire.set_lambda(y, [y_lam])

            #set y lam hat
            if str(n_mult) not in wire.lam_hat(y):
                lam_y_hat_var = generateNum(cipher, 'lambda y hat', n_mult) 
                wire.set_lam_hat(y, [lam_y_hat_var], n_mult)
            #set z lam 
            z_lam = generateNum(cipher, 'lambda', z)  
            wire.set_lambda(z, [z_lam])
            #set z lam hat 
            if str(n_mult) not in wire.lam_hat(z):
                lamzhat = generateNum(cipher, 'lambda z hat', n_mult)
                wire.set_lam_hat(z, [lamzhat], n_mult)
            n_mult += 1
      
        elif gate.operation == "INV" or gate.operation == "NOT":
            if x < n_input and lambda_val[x] == Value(None): 
                x_lam = generateNum(cipher, 'lambda', x)
                wire.set_lambda(x, [x_lam])
        
        #(new code)
        if gate.operation == "SCA":
            #calculate lambdas from PR generateNum
            if x < n_input and lambda_val[x] == Value(None):
                x_lam = generateNum(cipher, 'lambda', x)
                wire.set_lambda(x, [x_lam])

    return lambda_val, lambda_z, lam_y_hat, lam_z_hat