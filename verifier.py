import sys
import hashlib
from Value import Value
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
def rebuild_commitments(circuit, n_input, n_gates, parties, views, list_rval, broadcast, broadcast_rval):
    #rebuild commitments 
    rebuilt_views = [None]*len(parties) #list of views committed again via sha256 

    for i in range(len(views)):
        party = views[i]
        n_mul = 0
        input_str = b''
        input_lam_str = b''
        lam_z_str = b''
        lam_y_hat_str = b''
        lam_z_hat_str = b''
        for j in range(n_gates):
            c = circuit[j]
            if c.x < n_input:
                input_str += long_to_bytes(party['input'][c.x].value)
                input_lam_str += long_to_bytes(party['input lambda'][c.x].value)
            if c.y < n_input:
                pass
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
        assert(rebuilt_views[i] == committed_views[parties[i]])

    #check broadcast
    assert (hashlib.sha256(rebuilt_broadcast).hexdigest() == committed_broadcast)

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
    assert(sum(zeta) == check_zero)
    return 1 

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
        parties: list of parties opened 
        views: views opened by prover (parties[i] is the opened view[i])
        epsilon1, epsilon2: generated by fiat shamir 
        broadcast: open broadcast received in round 5
"""
def recompute(circuit, n_wires, n_gate, n_parties, parties, views, epsilon1, epsilon2, broadcast):
    alpha = []
    zeta_broadcast = [None]*len(parties)
    output_shares = []

    to_concatenate = n_wires - len(views[0]['input'])

    e_inputs = broadcast['e inputs'] + [Value(0)]*to_concatenate
    e_z = broadcast['e z']
    e_z_hat = broadcast['e z hat'] + [Value(0)]*to_concatenate
    p_alpha = broadcast['alpha']

    for i in range(len(parties)):
        num_mult = 0
        zeta = 0
        input_count = 0
        input_val = views[i]['input'] 
        lambda_val = views[i]['input lambda'] + ([Value(0)]*to_concatenate)
        lambda_z = views[i]['lambda z'] 
        lam_y_hat = views[i]['lambda y hat']
        lam_z_hat = views[i]['lambda z hat']
        wire_value = [input_val[i] if i < len(input_val) else Value(0) for i in range(n_wires)]        
        alpha_shares = []

        for j in range(n_gate):
            c = circuit[j]
            if c.operation == 'ADD' or c.operation == 'XOR':
                x_v = wire_value[c.x]
                y_v = wire_value[c.y]
                z_v = x_v + y_v
                lamx = lambda_val[c.x]
                lamy = lambda_val[c.y]
                wire_value[c.z] = z_v
                lambda_val[c.z] = lamx + lamy
                x_e, y_e = e_inputs[c.x], e_inputs[c.y]
                e_inputs[c.z] = x_e + y_e
            if c.operation == 'MUL' or c.operation == 'AND':
                x_v = wire_value[c.x]
                y_v = wire_value[c.y]
                if i == 0: 
                    z_v = e_z[num_mult] - lambda_z[num_mult]
                else:
                    z_v = Value(0) - lambda_z[num_mult]
                wire_value[c.z] = z_v
            
                e_inputs[c.z] = e_z[num_mult]
                lambda_val[c.z] = lambda_z[num_mult]

                y_lam = lambda_val[c.y]
                y_lamh = lam_y_hat[num_mult]
                alpha_to_share = epsilon1[num_mult]*y_lam + (epsilon2[num_mult] * y_lamh)
                alpha_shares.append(alpha_to_share)
                
                x = c.x
                y = c.y
                z = c.z
                A = sum(p_alpha[num_mult])

                zeta += (epsilon1[num_mult] * e_inputs[y] - A)* lambda_val[x] + \
                    epsilon1[num_mult] * e_inputs[x] * lambda_val[y] - \
                        epsilon1[num_mult] * lambda_z[num_mult] - epsilon2[num_mult] * lam_z_hat[num_mult]
                if i == 0: 
                    zeta += epsilon1[num_mult] * e_z[num_mult] - epsilon1[num_mult] * e_inputs[x] * e_inputs[y] + epsilon2[num_mult] * e_z_hat[num_mult]
                num_mult += 1
        zeta_broadcast[i] = zeta

        output_shares.append(wire_value[-1])
        alpha.append(alpha_shares)

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
            assert (prover_alpha[j][parties[i]].value == recomputed_alpha[i][j].value)
        assert(recompute_output_shares[i].value == prover_output[parties[i]].value)
        assert(recomputed_zeta[i].value == prover_zeta[parties[i]].value)

    return 1 


def verifier(committed_views, committed_broadcast, parties, views, broadcast):
    Circuit = circuit.parse(gate)
    n_wires = Circuit[4]
    n_gate = Circuit[3]
    l_input = Circuit[1]
    n_input = Circuit[6]
    n_output = Circuit[5]
    l_output = Circuit[2]
    n_mul = Circuit[8]
    Circuit = Circuit[0]

    # Create list of wire data
    n_parties = 3    
    wire_data = circuit.wire_data(n_wires)
    w = Wire(wire_data, n_parties, n_wires)