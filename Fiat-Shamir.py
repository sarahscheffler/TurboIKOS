"""
Perform the Fiat-Shamir transformation with SHA256 for non-interactive proof 
"""

from hashlib import sha256
from gmpy2 import mpz, t_mod, sub
from Crypto.Util.number import bytes_to_long
from binascii import hexlify
from random import sample, seed

field = mpz(2**127-1) #field value 
reject_value = sub(field, t_mod(field, 4)) #QUESTION: why are we breaking it into 4 equal parts? is there a reason? 

def make_epsilons(r2, num_mult_gates):
    """
    function will generate epsilsons for round2. verifier can call make epsilons to check that prover is not cheating, which is why make_epsilons is a separate 
    function rather than being nested in round2 

    inputs: r2 (from func round), num_mult_gates (number of mult gates for epsilon creation?) <-- either move this one to prover or get num of mult gates from another files
    outputs: 2*num_mult_gates epsilsons 
    """    
    list_epsilon = [0]*num_mult_gates
    for i in range(num_mult_gates):
        mid_value_1 = 0
        mid_value_2 = mid_value_1+1 

        temp_1 = bytes_to_long(sha256(str(i).encode() + str(mid_value_1).encode() + r2)) #hash(i || mid_value_1 || r2) --> coverted to long 
        temp_2 = bytes_to_long(sha256(str(i).encode() + str(mid_value_2).encode() + r2)) #hash(i || mid_value_2 || r2) --> coverted to long 

        epsilon = t_mod(mpz(temp_1), field)
        epsilon_hat = t_mod(mpz(temp_2), field)

        while epsilon > reject_value: #REJECTION SAMPLE epsilon, will reject and find new value if epsilon is greater than desired distribution value 
            mid_value_1 += 1
            temp_1 = bytes_to_long(sha256(str(i).encode() + str(mid_value_1).encode() + r2)) #hash(i || mid_value_1 || r2) --> coverted to long 
            epsilon = t_mod(mpz(temp_1), field)
        
        while epsilon_hat > reject_value: #REJECTION SAMPLE epsilon_hat, will reject and find new value if epsilon is greater than desired distribution value 
            mid_value_2 += 1
            temp_2 = bytes_to_long(sha256(str(i).encode() + str(mid_value_2).encode() + r2)) #hash(i || mid_value_1 || r2) --> coverted to long 
            epsilon_hat = t_mod(mpz(temp_2), field)


        list_epsilon[i] = [epsilon, epsilon_hat]
    return list_epsilon

def round2(round_1, num_mult_gates):
    """"
    inputs: round_1 (byte string of everything in round 1), num_mult_gates (int, utilized for calling make_epsilons)
    output: list of epsilons for round 3 
    """
    r2 = None
    if (type(round_1) == bytes): #checks that input is in the right format of <class 'bytes'>
        r2 = sha256(round_1)
    else: #else, encodes round_1 to satisfy type requirement 
        r2 = sha256(round_1.encode())

    return make_epsilons(r2, num_mult_gates)

    

def round4(round_1, round_3, t, n):
    """
    inputs: 
        round_1: binary/byte string of everything in round 1
        round_3: binary/byte string of everything in round 3
        t: number of parties to be corrupted 
        n: number of all parties 
    output: 
        list of parties #NOTE temporarily will use an array to send back, change after checking w prover 
    """

    #checks type of inputs for sha256 
    if type(round_1) == bytes and type(round_3) == bytes:
        r4 = (sha256(round_1 + round_3)) #sha256 (round_1 || round_3)
    else:
        if type(round_1) == bytes and type(round_3) != bytes:
            r4 = sha256(round_1 + round_3.encode())
        elif type(round_1) != bytes and type(round_3) == bytes:
            r4 = sha256(round_1.encode() + round_3) 
        else:
            r4 = sha256(round_1.encode() + round_3.encode())
    
    #generate parties for round 5 
    if t == (n-1): 
        do_not_open = t_mod(mpz(bytes_to_long(r4)), mpz(n)) 
        return [x for x in range(n) if x != do_not_open]
    else:
        list_parties = [x for x in range(field)]
        mid_value = 0 #TO DO: add rejection sample 
        temp = bytes_to_long(sha(str(i).encode() + str(mid_value).encode() + r4))
        seed(t_mod(mpz(temp), n)) #QUESTION i don't think this works? but wondering if something similar exists to set seed as value generated from hashed value 
        return sample(list_parties, t)
