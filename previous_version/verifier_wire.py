import sys
import hashlib
from Value import Value
from wire import Wire
import circuit as cpy
from Crypto.Util.number import bytes_to_long, long_to_bytes
import Fiat_Shamir
from wire import Wire
from gate import gate
from gmpy2 import mpz

"""
---check_commitments---
    inputs: 
        circuit: Circuit object
        n_input: number of inputs 
        n_gates: number of gates 
        parties: list of the party number opened by prover (generated from Fiat Shamir)
        list_rval: list the randomness used for each view commitment, same length as views, received in round 5
        broadcast: opened broadcast, received in round 5 
        broadvast_rval: randomness for broadcast, received in round 5
    output: 
        returns 1 if all assertions pass, else get assertion error 
"""
def rebuild_commitments(circuit, n_input, n_gates, parties, open_views, list_rval, broadcast, broadcast_rval):
    #rebuild commitments 
    rebuilt_views = [None]*len(parties) #list of views committed again via sha256 

    for i in range(len(open_views)):
        party = open_views[i]
        n_mul = 0
        input_str = b''
        input_lam_str = b''
        lam_z_str = b''
        lam_y_hat_str = b''
        lam_z_hat_str = b''
        for j in range(n_input):
            input_str += long_to_bytes(party['input'][j].value)
            input_lam_str += long_to_bytes(party['input lambda'][j].value)
        for j in range(n_gates):
            c = circuit[j]
            if c.operation == 'MUL' or c.operation == 'AND':
                lam_z_str += long_to_bytes(party['lambda z'][n_mul].value)
                lam_y_hat_str += long_to_bytes(party['lambda y hat'][n_mul].value)
                lam_z_hat_str += long_to_bytes(party['lambda z hat'][n_mul].value)
                n_mul += 1
                
        view_str_test = input_str + input_lam_str + lam_z_str + lam_y_hat_str + lam_z_hat_str
        view_str = long_to_bytes(list_rval[i]) + input_str + input_lam_str + lam_z_str + lam_y_hat_str + lam_z_hat_str
        rebuilt_views[i] = hashlib.sha256(view_str).hexdigest()
            

    #check that information from round 3 was not tampered with (broadcast to committed_broadcast)
    rebuilt_broadcast = b''
    for item in broadcast:
        if item == 'alpha':
            alpha_array = broadcast['alpha']
            n = len(alpha_array)
            m = len(alpha_array[0])
            for i in range(n):
                for j in range(m):
                    rebuilt_broadcast += long_to_bytes(alpha_array[i][j].value)
        else:
            for item_value in broadcast[item]:
                rebuilt_broadcast += long_to_bytes(item_value.value)
    rebuilt_broadcast = long_to_bytes(broadcast_rval) + rebuilt_broadcast

    return rebuilt_views, rebuilt_broadcast

"""
---check_commitments---
inputs: 
    parties: list of parties opened 
    committed_views: received from prover from round1
    rebuilt_views: rebuild_commitments()[0]
    committed_broadcast: received from prover round 1
    rebuilt_broadcast: rebuild_commitments()[1]
"""

def check_commitments(parties, committed_views, rebuilt_views, committed_broadcast, rebuilt_broadcast):
    #check views 
    for i in range(len(parties)):
        assert(rebuilt_views[i] == committed_views[parties[i]]), "Commitment view does not match opened view"

    #check broadcast
    assert (hashlib.sha256(rebuilt_broadcast).hexdigest() == committed_broadcast), "Committed broadcast does not match open broadcast"
    print("Prover's committed views and broadcast match the opened views and broadcast")
    return 1

"""
---check_zeta---
    inputs: 
        broadcast (dictionary)
    output: 
        return 1 if sum(zeta) == 0, else assertion error 
"""
def check_zeta(broadcast): 
    #check \zeta == 0
    check_zero = Value(0)
    zeta = broadcast['zeta']
    assert(sum(zeta) == check_zero), "Zeta does not sum to zero"
    print("Zetas in prover's broadcast sums to 0")
    return 

"""
---get_epsilons---
    inputs: 
        committed_views: committed views from round1 
        n_multgates: number of mult gates 
"""
def get_epsilons(committed_views, n_multgates):
    r2 = hashlib.sha256(committed_views)
    return Fiat_Shamir.make_epsilons(r2.digest(), n_multgates)

"""
---recompute---
    inputs:
        circuit: circuit object 
        n_wires: number of wires object
        n_gates: number of gates
        n_parties: number of parties 
        n_mult: number of mult gates 
        parties: list of parties opened 
        committed_views: commmitted views sent by prover in round 1
        open_views: views opened by prover (parties[i] is the opened view[i])
        broadcast: open broadcast received in round 5
"""
def recompute(circuit, n_wires, n_gate, n_parties, n_mult, parties, comitted_views, open_views, broadcast):
    none_arr = [Value(0)]*n_parties
    if_equal = Value()
    wire_data = [{'e': None, 'v': Value() , 'lambda': None, 'lam_hat': Value(), 'e_hat': None} for i in range(n_wires)]
    w = Wire(wire_data, n_parties, n_wires)

    e_inputs = broadcast['e inputs']
    e_z = broadcast['e z']
    e_z_hat = broadcast['e z hat']

    for i in range(len(parties)):
        num_mult = 0
        current_party = parties[i]
        input_val = open_views[i]['input'] 
        lambda_val = open_views[i]['input lambda']
        lambda_z = open_views[i]['lambda z'] 
        lam_y_hat = open_views[i]['lambda y hat']
        lam_z_hat = open_views[i]['lambda z hat']
        for j in range(n_gate):
            c = circuit[j]  
            if c.operation == 'ADD' or c.operation == 'XOR':
                if type(w.v(c.x)) != list:
                    w.set_v(c.x, none_arr) 
                if w.v(c.x)[current_party].value == 0:
                    w.v(c.x)[current_party] = input_val[c.x]
                if type(w.v(c.y)) != list:
                    w.set_v(c.y, none_arr) 
                if w.v(c.y)[current_party].value == 0:
                    w.v(c.y)[current_party] = input_val[c.y] 
                if w.lambda_val(c.x) == None:
                    w.set_lambda(c.x, none_arr)
                if w.lambda_val(c.x)[current_party].value == 0:
                    w.lambda_val(c.x)[current_party] = lambda_val[c.x]
                if w.lambda_val(c.y) == None:
                    w.set_lambda(c.y, none_arr)
                if w.lambda_val(c.y)[current_party].value == 0:
                    w.lambda_val(c.y)[current_party] = lambda_val[c.y]
                if c.x < len(e_inputs):
                    w.set_e(c.x, e_inputs[c.x]) 
                if c.y < len(e_inputs):
                    w.set_e(c.y, e_inputs[c.y])
            if c.operation == "MUL" or c.operation == "AND":
                if type(w.v(c.x)) != list:
                    w.set_v(c.x, none_arr)
                if w.v(c.x)[current_party].value == 0:
                    w.v(c.x)[current_party] = input_val[c.x]
                if type(w.v(c.y)) != list:
                    w.set_v(c.y, none_arr) 
                if w.v(c.y)[current_party].value == 0:
                    w.v(c.y)[current_party] = input_val[c.y] 
                w.set_e(c.z, e_z[num_mult])
                if w.lambda_val(c.x) == None:
                    w.set_lambda(c.x, none_arr)
                if w.lambda_val(c.x)[current_party].value == None:
                    w.lambda_val(c.x)[current_party] = lambda_val[c.x]
                if w.lambda_val(c.z) == None:
                    w.set_lambda(c.z, none_arr)
                if w.lambda_val(c.z)[current_party].value == 0:
                    w.lambda_val(c.z)[current_party] = lambda_z[num_mult]
                if w.lambda_val(c.y) == None:
                    w.set_lambda(c.y, none_arr)
                if w.lambda_val(c.y)[current_party].value == 0:
                    w.lambda_val(c.y)[current_party] = lambda_val[c.y]
                if type(w.lam_hat(c.y)) != list:
                    w.set_lam_hat(c.y, none_arr)
                if w.lam_hat(c.y)[current_party].value == 0:
                    w.lam_hat(c.y)[current_party] = lam_y_hat[num_mult]
                if c.x < len(e_inputs):
                    w.set_e(c.x, e_inputs[c.x]) 
                if c.y < len(e_inputs):
                    w.set_e(c.y, e_inputs[c.y])
                w.set_e_hat(c.z, e_z_hat[num_mult])
                num_mult += 1

    temp_str = ''.join(comitted_views)
    temp_epsilon = get_epsilons(temp_str.encode(), n_mult)
    epsilon1 = temp_epsilon[0]
    epsilon2 = temp_epsilon[1]

    p_alpha = broadcast['alpha']

    alpha = cpy.compute_output(circuit, epsilon1, epsilon2, w, n_gate, n_parties)
    zeta_broadcast = cpy.compute_zeta_share(circuit, w, p_alpha, epsilon1, epsilon2, n_parties)

    output_shares = w.v(circuit[-1].z)

    return alpha, output_shares, zeta_broadcast

"""
---check_recompute---
inputs:
    parties: list of parties that were opened 
    n_multgate: number of mult gates
    broadcast: broadcast channel received in round 5 
    recomputed_alphas: recompute()[0], row # = party, column # = multgate 
    recomputed_output_shares = recompute()[1]
    recomputed_zetas: recompute()[2]
"""
def check_recompute(parties, n_multgate, broadcast, recomputed_alpha, recompute_output_shares, recomputed_zeta):
    prover_alpha = broadcast['alpha']
    prover_output = broadcast['output shares']
    prover_zeta = broadcast['zeta']

    for i in range(len(parties)): 
        #check alphas 
        for j in range(n_multgate):
            assert (prover_alpha[j][parties[i]].value == recomputed_alpha[i][j].value), "Verifier's recomputed alphas does not match prover's alphas."
        assert(recompute_output_shares[i].value == prover_output[parties[i]].value), "Verifier's recomputed output shares does not match prover's output shares."
        assert(recomputed_zeta[i].value == prover_zeta[parties[i]].value), "Verifier's recomputd zetas does not match prover's zetas."

    print("Verifier's alphas, zetas, and output matches prover's.")
    return 


def verifier():
    pass