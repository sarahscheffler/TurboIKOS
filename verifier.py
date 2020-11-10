import sys
import hashlib
from Value import Value
from Cryptodome.Util.number import bytes_to_long, long_to_bytes
import Fiat_Shamir
from wire import Wire
from gate import gate
from gmpy2 import mpz
import Preprocessing as prepro
import circuit as CTEST

"""
---check_commitments----
    inputs: 
        circuit: Circuit object
        c_info: dictionary of information extracted from circuit.parse -- look at circuit for how dictionary is set up 
        parties: list of the party number opened by prover (generated from Fiat Shamir)
        open_views: party views opened by prover (round 5)
        list_rval: list the randomness used for each view commitment, same length as views, received in round 5
        broadcast: opened broadcast, received in round 5 
        broadvast_rval: randomness for broadcast, received in round 5
    output: 
        returns 1 if all assertions pass, else get assertion error 
"""
def rebuild_commitments(circuit, c_info, parties, open_views, list_rval, broadcast, broadcast_rval):
    n_input, n_gate = c_info['n_input'], c_info['n_gate']
    #rebuild commitments 
    rebuilt_views = [None]*len(parties) #list of views committed again via sha256 

    for i in range(len(open_views)):
        party = open_views[i]
        n_mul = 0
        input_str = b''
        lambda_seed = b''
        lambda_seed += (party['party seed'])
        for j in range(n_input):
            input_str += long_to_bytes(party['input'][j].value)
                
        view_str_test = input_str + lambda_seed
        view_str = long_to_bytes(list_rval[i]) + input_str + lambda_seed
        rebuilt_views[i] = hashlib.sha256(view_str).hexdigest()
            

    #check that information from round 3 was not tampered with (broadcast to committed_broadcast)
    rebuilt_broadcast = b''
    for item in broadcast:
        if item == 'alpha':
            alpha_array = broadcast['alpha']
            n = len(alpha_array)
            l = len(alpha_array[0])
            m = len(alpha_array[0][0])
            for e in range(l):
                for i in range(n):
                    for j in range(m):
                        rebuilt_broadcast += long_to_bytes(alpha_array[i][e][j].value)
        elif item == 'zeta':
            zeta_array = broadcast['zeta']
            for i in range(len(zeta_array)):
                for j in range(len(zeta_array[0])):
                    rebuilt_broadcast += long_to_bytes(zeta_array[i][j].value)
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
    # print("Prover's committed views and broadcast match the opened views and broadcast")
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
    for e in range(len(zeta)):
        assert(sum(zeta[e]) == check_zero), "Zeta does not sum to zero"
    return 

"""
---NEW PROTOCOL: check_alpha---
    broadcast3: third broadcast committed in rount 5 opened in round 7
"""
def check_bigalpha(broadcast3): 
    check_zero = Value(0)
    for e in range(len(broadcast3)):
        assert(sum(broadcast3[e]) == check_zero), "Big Alpha does not sum to zero"
    return

"""
---get_epsilons---
    inputs: 
        committed_views: committed views from round1 
        n_multgates: number of mult gates 
"""
def get_epsilons(committed_views, n_multgates, n_epsilons):
    r2 = hashlib.sha256(committed_views)
    return Fiat_Shamir.make_epsilons(r2.digest(), n_multgates, n_epsilons)

"""
NEW PROTOCOL 
"""
def get_gammas_ehat(commited_round3, n_multgates):
    r3 = hashlib.sha256(commited_round3)
    return Fiat_Shamir.make_gammas(r3.digest(), n_multgates)

"""
---recompute---
    inputs:
        circuit: circuit object 
        c_info: dictionary of information extracted from circuit.parse -- look at circuit for how dictionary is set up 
        n_parties: number of parties 
        parties: list of parties opened 
        committed_views: commmitted views sent by prover in round 1
        open_views: views opened by prover (parties[i] is the opened view[i])
        broadcast: open broadcast received in round 5
"""
def recompute(circuit, c_info, n_parties, parties, comitted_views, open_views, broadcast, commit_round3):
    #get info from c_info
    n_wires, n_gate, n_mult = c_info['n_wires'], c_info['n_gate'], c_info['n_mul']
    #get epsilons 
    temp_str = ''.join(comitted_views)
    temp_epsilon = get_epsilons(temp_str.encode(), n_mult)
    epsilon1 = temp_epsilon[0]
    epsilon2 = temp_epsilon[1]

    #get gammas
    temp_gammas = get_gammas_ehat(commit_round3, n_mult)
    gammas = temp_gammas[0]

    #initialize empty lists and other information 
    alpha = [[None for x in range(len(parties))] for x in range(n_mult)]
    zeta_broadcast = [None for x in range (len(parties))]
    output_shares = []
    to_concatenate = n_wires - len(open_views[0]['input'])

    e_inputs = broadcast['e inputs'] + [Value(0)]*to_concatenate
    e_z = broadcast['e z']
    e_z_hat = broadcast['e z hat'] + [Value(0)]*to_concatenate
    p_alpha = broadcast['alpha'] #little alpha 

    output_test = [] #output test 
    bigA = []

    for i in range(len(parties)):
        current_party = parties[i]
        party_view = open_views[i]
        seed = party_view['party seed']

        input_val = open_views[i]['input'] 
        wire_value = [input_val[k] if k < len(input_val) else Value(0) for k in range(n_wires)]        

        #generating lambdas from the master seed 
        rebuild_lam = prepro.rebuildlambda(current_party, seed, circuit, c_info)
        lambda_val = rebuild_lam[0] + ([Value(0)]*to_concatenate)
        lambda_z = rebuild_lam[1]
        lam_y_hat = rebuild_lam[2]
        lam_z_hat = rebuild_lam[3]
        alpha_shares = []
        tempbigA = []

        outputs = []
        num_mult = 0
        zeta = 0
        for j in range(n_gate):
            c = circuit[j]
            if c.operation == 'ADD' or c.operation == 'XOR':
                if e == 0:
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
                # x_v = wire_value[c.x]
                # y_v = wire_value[c.y]
                if parties[i] == 0: 
                    z_v = e_z[num_mult] - lambda_z[num_mult]
                else:
                    z_v = Value(0) - lambda_z[num_mult]
                wire_value[c.z] = z_v    
        
                e_inputs[c.z] = e_z[num_mult]
                lambda_val[c.z] = lambda_z[num_mult]

                y_lam = lambda_val[c.y]
                y_lamh = lam_y_hat[str(num_mult)]

                x = c.x
                y = c.y
                z = c.z
                # epsilon1[e][num_mult], y_lam, epsilon2[e][num_mult], y_lamh
                alpha_to_share = epsilon1[num_mult]*y_lam + (epsilon2[num_mult] * y_lamh)
                alpha[num_mult][e][i] = alpha_to_share #alpha[nummult][epsilon]
        
                A = sum(p_alpha[num_mult])
                zeta += (epsilon1[num_mult] * e_inputs[y] - A)* lambda_val[x] + \
                        epsilon1[num_mult] * e_inputs[x] * lambda_val[y] - \
                        epsilon1[num_mult] * lambda_z[num_mult] - epsilon2[num_mult] * lam_z_hat[str(num_mult)]
                
                if parties[i] == 0: 
                    #epsilon1[e][num_mult], e_z[num_mult], epsilon1[e][num_mult], e_inputs[x], e_inputs[y], epsilon2[e][num_mult]e_z_hat[num_mult]
                    zeta += epsilon1[num_mult] * e_z[num_mult] - epsilon1[num_mult] * e_inputs[x] * e_inputs[y] + epsilon2[num_mult] * e_z_hat[num_mult]
                
                num_mult += 1
            if c.operation == 'INV' or c.operation == 'NOT': 
                if current_party == 0:
                    wire_value[c.z] = wire_value[c.x] + Value(1)
                    lambda_val[c.z] = lambda_val[c.x] + Value(1) 
                else:
                    wire_value[c.z] = wire_value[c.x]
                    lambda_val[c.z] = lambda_val[c.x]
                    e_inputs[c.z] = e_inputs[c.x]

            if j == n_gate-1:
                zeta_broadcast[i] = zeta
            outputs.append(wire_value[c.z])

        # output_shares.append(wire_value[-1]) #no clue why THIS doesn't work? 
        output_shares.append(outputs[-1])
        output_test.append(outputs)

    for p in range(parties): 
        for e in range(n_epsilons):
            sum_smalla = 0 
            for m in range(n_mult):
                sum_smalla += (gammas[p] * alpha[m][e][p])
                if p == 0:
                    sum_smalla -= (gammas[p]*)


    return alpha, output_shares, zeta_broadcast #REMOVE OUTPUTS

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
def check_recompute(c_info, parties, broadcast, recomputed_alpha, recompute_output_shares, recomputed_zeta, n_epsilons):
    n_multgate = c_info['n_mul']
    prover_alpha = broadcast['alpha']
    prover_output = broadcast['output shares']
    prover_zeta = broadcast['zeta']

    for i in range(len(parties)): 
        #check alphas 
        assert(recompute_output_shares[i].value == prover_output[parties[i]].value), "Verifier's recomputed output shares does not match prover's output shares."
        for e in range(n_epsilons):
            for j in range(n_multgate):
                assert (prover_alpha[j][e][parties[i]].value == recomputed_alpha[j][e][i].value), "Verifier's recomputed alphas does not match prover's alphas."
                assert(recomputed_zeta[e][i].value == prover_zeta[e][parties[i]].value), "Verifier's recomputed zetas does not match prover's zetas."

    # print("Verifier's alphas, zetas, and output matches prover's.")
    return 


def verifier(circuit, c_info, n_parties, parties, committed_views, open_views, r_views, committed_broadcast, broadcast, r_broadcast, n_epsilons):
    #check commitments
    rebuild = rebuild_commitments(circuit, c_info, parties, open_views, r_views, broadcast, r_broadcast)
    check_commitment = check_commitments(parties, committed_views, rebuild[0], committed_broadcast, rebuild[1])

    #verifier check zeta 
    check_zeta(broadcast)

    #verifier recompute 
    v_recompute = recompute(circuit, c_info, n_parties, parties, committed_views, open_views, broadcast, n_epsilons)

    checkrecompute = check_recompute(c_info, parties, broadcast, v_recompute[0], v_recompute[1], v_recompute[2], n_epsilons)
    print("passed")
