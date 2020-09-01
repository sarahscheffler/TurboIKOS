from secrets import token_bytes

import sys
import hashlib
from Value import Value
from Crypto.Util.number import bytes_to_long, long_to_bytes
import Fiat_Shamir
from wire import Wire
from gate import gate

"""
---check_commitments---
    inputs: 
        committed_views: list of all committed views, received in round1
        committed_broadcast: hashed broadcast, received in round 3
        parties: list of the party number opened by prover (generated from Fiat Shamir)
        list_rval: list the randomness used for each view commitment, same length as views, received in round 5
        views: list of opened party views, views[i] will correspond to parties[i] number, received in round 5
        broadcast: opened broadcast, received in round 5 
        broadvast_rval: randomness for broadcast, received in round 5

    output: 
        returns 1 if all assertions pass, else get assertion error 
"""
def check_commitments(committed_views, committed_broadcast, parties, views, list_rval, broadcast, broadcast_rval):
    #check that information from round 1 was not tampered with (views to committed_views)
    check_views = [None]*len(parties) #list of views committed again via sha256 

    for i in range(len(views)):
        input_str = b''
        input_lam_str = b''
        lam_z_str = b''
        lam_y_hat_str = b''
        lam_z_hat_str = b''
        for party in view:
            for item in party:
                if item == 'input':
                    for item_value in item:
                        input_str += long_to_bytes(item_value.value)
                if item == 'input lambda':
                    for item_value in item:
                        input_lam_str += long_to_bytes(item_value.value)
                if item == 'lambda z':
                    for item_value in item:
                        lam_z_str += long_to_bytes(item_value.value)
                if item == 'lambda y hat':
                    for item_value in item:
                        lam_y_hat_str += long_to_bytes(item_value.value)
                if item == 'lambda z hat':
                    for item_value in item:
                        lam_z_hat_str += long_to_bytes(item_value.value)
        view_str = list_rval[i] + input_str + input_lam_str + lam_z_str + lam_y_hat_str + lam_z_hat_str
        check_views[i] = hashlib.sha256(view_str)
            

    #check that information from round 3 was not tampered with (broadcast to committed_broadcast)
    round_3_check = b''
    for item in broadcast:
        if item == 'alpha':
            alpha_array = broadcast['alpha']
            n = len(alpha_array)
            m = len(alpha_array[0])
            for i in range(n):
                for j in range(m):
                    round_3_check += long_to_bytes(alpha_array[i][j].value)
        else:
            for item_value in item:
                round_3_check += long_to_bytes(item_value.value)
    round_3_check = broadcast_rval + round_3_check

    #check views 
    for i in range(len(check_views)):
        assert(check_views[i] == committed_views[parties[i]])

    #check broadcast
    assert (hashlib.sha256(round_3_check).hexdigest() == committed_broadcast) 

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
    
"""
def get_epsilons(committed_views, n_multgates):
    r2 = hashlib.sha256(committed_views)
    return Fiat_Shamir.make_epsilons(r2, n_multgates)

"""
---recompute---
    inputs:
        circuit: circuit object 
        wire: wire object
        n_gates: number of gates
        parties: list of parties opened 
        views: views opened by prover (parties[i] is the opened view[i])
        broadcast: open broadcast received in round 5
        epsilon1, epsilon2: generated by fiat shamir 
"""
def recompute(circuit, n_wires, n_gate, n_parties, parties, views, epsilon1, epsilon2):
    #recompute 
    recomputation = None
    # e_inputs = [0]*n_wires
    # e_z = [0]*n_wires
    # e_z_hat = [0]*n_wires
    alpha = []
    zeta_broadcast = []*n_parties
    output_shares = []

    num_mult = 0
    for i in range(len(parties)):
        e_inputs = [0]*n_wires
        e_z = []
        e_z_hat = []
        party_ouput_share = []
        input_val = views[i]['input']
        lambda_val = views[i]['input lambda']
        lambda_z = views[i]['lambda z']
        lam_y_hat = views[i]['lambda y hat']
        lam_z_hat = [view][i]['lambda z hat']
        wire_value = [input_val[i] if i < len(input_val) else 0 for i in range(n_gate)]        
        alpha_shares = []

        for j in range(n_gate):
            c = circuit[j]
            if c.operation == 'ADD' or c.operation == 'XOR':
                x_v = wire_value[c.x]
                y_v = wire_value[c.y]
                #calculate z_v 
                z_v = x_v + y_v
                wire_value[c.z] = z_v
                #calculate z_e 
                x_e = e_inputs[c.x]
                y_e = e_inputs[c.y]
                if not x_e:    
                    x_e = x_v + lambda_val[c.x]
                    e_inputs[c.x] = (x_e)
                if not y_e:  
                    y_e = y_v + lambda_val[c.y]
                    e_inputs[c.y] = (y_e)
                z_e = x_e + y_e
                e_inputs[c.z] = (z_e)
            if c.operation == 'MUL' or c.operation == 'AND':
                x_v = wire_value[c.x]
                y_v = wire_value[c.y]
                #calculate z_vi? 
                x_e = e_inputs[c.x]
                y_e = e_inputs[c.y]
                if not x_e:
                    x_lam = lambda_val[c.x] 
                    x_e = x_v + x_lam
                    e_inputs[c.x] = x_e
                if not y_e:
                    y_lam = lambda_val[c.y]
                    y_e = y_v + y_lam
                    e_inputs[c.y] = y_e
                #calculate z_e 
                z_v = x_v * y_v
                z_e = z_v + (lambda_z[num_mult])
                e_z.append(z_e)
                #calculate and set z_eh
                z_eh = lambda_val[c.x] * lam_y_hat[num_mult] * lam_z_hat[num_mult]
                e_z_hat.append(z_eh)
                if i == 0:
                    z_v_share = z_e - lambda_z[num_mult]
                else:
                    z_v_share = Value(0) - lambda_z[num_mult]
                wire_value[c.z] = z_v_share
                #calculate alpha shares
                y_lam = lambda_val[c.y]
                y_lamh = lam_y_hat[c.y]
                alpha_to_share = epsilon1[num_mult]*y_lam + (epsilon2[num_mult] * y_lamh)
                alpha_shares.append(alpha_to_share)
                num_mult += 1
            party_output_shares.append(wire_value[c.z])
        alpha.append(alpha_shares)
        output_shares.append(party_ouput_share)
        #calculate zeta 
        zeta = 0 
        n = 0
        for j in range(n_gate):
            c = circuit[j]
            if c.operation == 'MUL' or c.operation == 'AND':
                x = wire_value[c.x]
                y = wire_value[c.y]
                z = wire_value[c.z]
                A = sum(alpha[n])
                zeta += (epsilon1[n] * e_inputs[y] - A)*lambda_val[x] + \
                    epsilon1[n] * e_inputs[x] * lambda_val[y] - \
                        epsilon1[n] * lambda_z[z] - epsilon2[n] *lam_z_hat[n]

                if i == 0:
                    zeta += epsilon1[n] * e_z[n] - epsilon1[n]*e_inputs[x]*e_inputs[y] + epsilon2[n]*e_z_hat[n]
                n += 1
        zeta_broadcast[i] = zeta

    return alpha, zeta_broadcast, output_shares

"""
---check_recompute---
inputs:
    parties: list of parties that were opened 
    n_multgate: number of mult gates
    broadcast: broadcast channel received in round 5 
    recomputed_alphas: recompute()[0], row # = party, column # = multgate 
    recomputed_zetas: recompute()[1]
"""
def check_recompute(parties, n_multgate, broadcast, recomputed_alpha, recomputed_zetas):
    prover_alpha = broadcast['alpha']
    prover_zeta = broadcast['zeta']
    # prover_output = broadcast['output shares']
    for i in range(len(parties)): 
        #check alphas 
        for j in range(n_multgate):
            assert (prover_alpha[j][parties[i]].value == recomputed_alpha[i][j].value)

        #check zeta
        assert(recomputed_zetas[i] == prover_zeta[parties[i]])        
    return 1 


def verifier():
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
    