"""
Perform the fiat-shamir transformation with SHA256 for non-interactive proof 
"""

from hashlib import sha256
from gmpy2 import mpz, c_mod
from Crypto.Util.number import bytes_to_long
from binascii import hexlify

field = mpz(2**127-1)

def round2(round_1):
    """"
    inputs: round_1 (byte string of everything in round 1) 
    output: r2 (hashed value of round_1), used for epsilons 
    """
    #TODO: insert conditional to check type of input 
    return sha256(round_1)

def make_epsilons(r2, num_mult_gates):
    """
    inputs: r2 (from func round), num_mult_gates (number of mult gates for epsilon creation?) <-- either move this one to prover or get num of mult gates from another files
    outputs: 2*num_mult_gates epsilsons 
    """    
    list_epsilon = [0]*num_mult_gates
    for i in range(num_mult_gates):
        mid_value_1 = 0
        mid_value_2 = 1
        #TO DO: Rejection Sample 
        temp_1 = bytes_to_long(sha256(str(i).encode() + str(mid_value_1).encode() + r2)) #hash(i || mid_value_1 || r2) --> coverted to long 
        temp_2 = bytes_to_long(sha256(str(i).encode() + str(mid_value_2).encode() + r2)) #hash(i || mid_value_2 || r2) --> coverted to long 

        epsilon = c_mod(mpz(temp_1), field)
        epsilon_hat = c_mod(mpz(temp_2), field)

        list_epsilon[i] = [epsilon, epsilon_hat]
    return list_epsilon

def round4(round_1, round_3, t, n):
    """
    inputs: 
        round_1: binary/byte string of everything in round 1
        round_3: binary/byte string of everything in round 3
        t: number of parties to be corrupted 
        n: number of all parties 
    """
    #TO DO: check on what type round_1 and round_3 will be passed in as 
    r4 = (sha256(round_1 + round_3)) #sha256 (round_1 || round_3) and convert byte string into 
    #TO DO: add rejection sample 
    if t == (n-1):
        return c_mod(mpz(bytes_to_long(r4)), mpz(n))
    else:
        parties_to_corrupt = [0]*t
        for i in range(t): #similar to make_epsilons 
            mid_value = 0 #TO DO: add rejection sample 
            temp = bytes_to_long(sha(str(i).encode() + str(mid_value).encode() + r4))
            parties_to_corrupt[i] = c_mod(mpz(temp), n) #QUESTION: have to add something to prevent collision? 
        return parties_to_corrupt
