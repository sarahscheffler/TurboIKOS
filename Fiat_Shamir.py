"""
Perform the Fiat-Shamir transformation with SHA256 for non-interactive proof 
"""
import Value as v
from Value import Value
from binascii import hexlify
from hashlib import sha256
from random import sample, seed, getrandbits
from Cryptodome.Util.Padding import pad
from Cryptodome.Util.number import bytes_to_long
from gmpy2 import mpz, sub, t_mod
from circuit import n_epsilons

field = v.getfield()

"""
function will generate epsilsons for round2. verifier can call make epsilons to check that prover is not cheating, which is why make_epsilons is a separate 
function rather than being nested in round2 
inputs: r2 (from func round), num_mult_gates (number of mult gates for epsilon creation?) <-- either move this one to prover or get num of mult gates from another files
outputs: 2*num_mult_gates epsilsons*num_epsilons 
"""
def make_epsilons(r2, num_mult_gates):
    list_epsilon = [0 for x in range(num_mult_gates)]
    list_epsilon_hat = [0 for x in range(num_mult_gates)]
    seed(r2)
    #generate 128 random bits by using random.getrandbits, splice value 
    for i in range(num_mult_gates):
        epsilon = bin(getrandbits(127))
        epsilon_hat = bin(getrandbits(127))
        epsilon = Value(int(epsilon, 2))
        epsilon_hat = Value(int(epsilon_hat, 2))
        list_epsilon[i] = epsilon
        list_epsilon_hat[i] = epsilon_hat
    return list_epsilon, list_epsilon_hat

def make_gammas(round_3, num_mult_gates): #new protocol; have to add epsilon hat 
    list_gammas = [0 for x in range(num_mult_gates)] #list_gammas[#mult_gate]
    list_epsilonhat = [0 for x in range(num_mult_gates)] #list_gammas[#mult_gate]
    seed(round_3)
    for i in range(num_mult_gates):
        gamma = bin(getrandbits(127))
        epsilon_hat = bin(getrandbits(127))
        list_gammas[i] = Value(int(gamma,2))
        list_epsilonhat[i] = Value(int(epsilon_hat,2))
    return list_gammas, list_epsilonhat

""""
inputs: round_1 (byte string of everything in round 1), num_mult_gates (int, utilized for calling make_epsilons)
output: list of epsilons for round 3 
"""
def round2(round_1, num_mult_gates):
    r2 = None
    if (type(round_1) == bytes): 
        r2 = sha256(round_1)
    else:
        r2 = sha256(round_1.encode())

    return make_epsilons(r2.digest(), num_mult_gates)

def round_4(round3, num_mult_gates): 
    if (type(round3) == bytes):
        r3 = sha256(round3)
    else: 
        r3 = sha256(round3.encode())
    return make_gammas(r3.digest(), num_mult_gates)

"""
inputs: 
    round_1: binary/byte string of everything in round 1
    round_3: binary/byte string of everything in round 3
    t: number of parties to be corrupted 
    n: number of all parties 
output: 
    list of parties 
"""
def round6(round_1, round_3, t, n): #updated round6, generates list of parties to open 
    #checks type of inputs for sha256 
    if type(round_1) == bytes and type(round_3) == bytes:
        r4 = (sha256(round_1 + round_3)) #sha256 (round_1 || round_3)
    else:
        if type(round_1) == bytes and type(round_3) != bytes:
            r4 = sha256(round_1 + round_3.encode()).digest()
        elif type(round_1) != bytes and type(round_3) == bytes:
            r4 = sha256(round_1.encode() + round_3).digest() 
        else:
            r4 = sha256(round_1.encode() + round_3.encode()).digest()

    #generate parties for round 5 
    if t == (n-1): 
        do_not_open = t_mod(mpz(bytes_to_long(r4)), mpz(n)) 
        return [x for x in range(n) if x != do_not_open]
    else:
        list_parties = [x for x in range(n)]
        hash_value = r4
        seed(hash_value) 
        return sample(list_parties, t)
