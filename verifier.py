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

#input: circuit (circuit object), c_info (dict of circuit info), open_parties (list of open parties)
#       open_views (list of open views), dict_rval (dictionary of rvals), dict_broadcast (dictionary of broadcasts)
def rebuild_commitments(circuit, c_info, open_parties, open_views, dict_rval, dict_broadcast): 
    n_input, n_gate = c_info['n_input'], c_info['n_gate']

    #rebuild views 
    rebuilt_views = [None]*len(open_parties)
    views_rval = dict_rval['views']
    for i in range(len(open_views)): 
        party = open_views[i]
        n_mul = 0 
        input_str = b''
        lambda_seed_str = party['party seed']
        for j in range(n_input):
            input_str += long_to_bytes(party['input'][j].value)
        
        temp_str = long_to_bytes(views_rval[i]) + input_str + lambda_seed_str
        rebuilt_views[i] = hashlib.sha256(temp_str).hexdigest()

    #rebuild broadcasts 
    round1, round3, round5 = dict_broadcast['round1'], dict_broadcast['round3'], dict_broadcast['round5']
    r_round1, r_round3, r_round5 = dict_rval['round1'], dict_rval['round3'], dict_rval['round5']

    #round1
    temp_round1 = b'' 
    for item in round1: 
        for item_value in round1[item]:
            temp_round1 += long_to_bytes(item_value.value)
    temp_round1 = long_to_bytes(r_round1) + temp_round1
    rb_round1 = hashlib.sha256(temp_round1).hexdigest() #rebuild round1

    #round3
    temp_round3 = b''
    for item in round3: 
        for item_value in round3[item]:
            temp_round3 += long_to_bytes(item_value.value)
    temp_round3 = long_to_bytes(r_round3) + temp_round3
    rb_round3 = hashlib.sha256(temp_round3).hexdigest() #rebuilt round3

    temp_round5 = b'' 
    for item_value in round5:
        temp_round5 += long_to_bytes(item_value.value)
    temp_round5 = long_to_bytes(r_round5) + temp_round5
    rb_round5 = hashlib.sha256(temp_round5).hexdigest() #rebuilt round5

    dict_rebuilt = {'views': rebuilt_views, 'round1': rb_round1, 'round3': rb_round3, 'round5': rb_round5}

    return dict_rebuilt

#INPUT: parties (list of open parties), cm_views (committed views), cm_round1 (committed round 1 broadcast), cm_round3 (committed round 3 broadcast)
#       cm_round5(committed round 5 broadcast), dict_rebuilt (dictionary of rebuilt commitments from rebuild_commitments)

def check_commitments(parties, cm_views, cm_broadcast1, cm_round3, cm_round5, dict_rebuilt): 
    #check views 
    rb_views = dict_rebuilt['views']
    for i in range(len(parties)):
        assert(rb_views[i] == cm_views[parties[i]]), "Committed views does not match opened view"
    
    #check round1
    rb_round1 = dict_rebuilt['round1']
    assert(rb_round1 == cm_broadcast1), "Committed round 1 broadcast does not match opened round 1 broadcast"
    #check round 3
    rb_round3 = dict_rebuilt['round3']
    assert(rb_round3 == cm_round3), "Committed round 3 broadcast does not match opened round 3 broadcast"
    #check round 5
    rb_round5 = dict_rebuilt['round5']
    assert(rb_round5 == cm_round5), "Committed round 5 broadcast does not match opened round 5 broadcast"
    return

"""
---check_zeta---
    inputs: 
        broadcast (dictionary)
    output: 
        return 1 if sum(zeta) == 0, else assertion error 
"""
def check_zeta(broadcast): #round three broadcast
    #check \zeta == 0
    check_zero = Value(0)
    zeta = broadcast['zeta']
    assert(sum(zeta) == check_zero), "Zeta does not sum to zero"
    return 

"""
---NEW PROTOCOL: check_alpha---
    broadcast3: third broadcast committed in rount 5 opened in round 7
"""
def check_bigalpha(round5): #round 5 broadcast
    check_zero = Value(0)
    assert(sum(round5) == check_zero), "Big Alpha does not sum to zero"
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
def recompute(circuit, c_info, parties, comitted_views, committed_broadcast1, open_views, open_round1, open_round3, commit_round3):
    #get info from c_info
    n_wires, n_gate, n_mult = c_info['n_wires'], c_info['n_gate'], c_info['n_mul']
    #get epsilons 
    temp_str = ''.join(comitted_views) + committed_broadcast1
    temp_epsilon = get_epsilons(temp_str.encode(), n_mult)
    epsilon1 = temp_epsilon[0]
    epsilon2 = temp_epsilon[1]

    #get gammas
    temp_gammas = get_gammas_ehat(commit_round3.encode(), n_mult)
    gammas = temp_gammas[0]

    #initialize empty lists and other information 
    alpha_shares = [[None for x in range(len(parties))] for x in range(n_mult)] #alpha[mult gate][party]
    zeta_broadcast = [None for x in range (len(parties))]
    output_shares = []
    to_concatenate = n_wires - len(open_views[0]['input'])

    e_inputs = open_round1['e inputs'] + [Value(0)]*to_concatenate
    e_z = open_round1['e z']
    e_z_hat = open_round1['e z hat'] + [Value(0)]*to_concatenate

    b_alpha = open_round3['little_alpha'] #broadcast_alpha

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

        outputs = []
        num_mult = 0
        zeta = 0
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
                
                alpha_shares[num_mult][i] = epsilon1[num_mult]*y_lam + (epsilon2[num_mult] * y_lamh) #alpha[nummult][party]
                A = b_alpha[num_mult]
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
    


    bigA = [None for x in range(len(parties))]
    for p in range(len(parties)): 
        sum_smalla = 0 
        for m in range(n_mult):
            sum_smalla += (gammas[m] * alpha_shares[m][p])
            if parties[p] == 0:
                sum_smalla -= (gammas[m]*b_alpha[m])
        bigA[p] = sum_smalla
    return bigA, output_shares, zeta_broadcast #REMOVE OUTPUTS

"""
---check_recompute---
inputs:
    c_info: dictionary of circuit info 
    parties: list of open parties 
    dict_broadcast: dictionary of broadcasts from round1, round3, round5
    recomputed_alpha: recompute[0]
    recompute_output_shares = recompute[1]
    recomputed_zeta = recompute[2]
"""
def check_recompute(c_info, parties, dict_broadcast, recompute_A, recompute_output_shares, recomputed_zeta):
    n_multgate = c_info['n_mul']
    prover_alpha = dict_broadcast['round5']
    prover_output = dict_broadcast['round1']['output shares']
    prover_zeta = dict_broadcast['round3']['zeta']

    for i in range(len(parties)): 
        current_party = parties[i]
        #check alphas 
        assert(recompute_output_shares[i].value == prover_output[current_party].value), "Verifier's recomputed output shares does not match prover's output shares."
        assert (prover_alpha[current_party].value == recompute_A[i].value), "Verifier's recomputed alphas does not match prover's big alphas."
        assert(recomputed_zeta[i].value == prover_zeta[current_party].value), "Verifier's recomputed zetas does not match prover's zetas."

    # print("Verifier's alphas, zetas, and output matches prover's.")
    return 


def verifier(circuit, c_info, parties, cm_views, cm_broadcast1, cm_round3, cm_round5, open_views, dict_rval, dict_broadcast):
    #check commitments
    rebuild = rebuild_commitments(circuit, c_info, parties, open_views, dict_rval, dict_broadcast)
    check_commitment = check_commitments(parties, cm_views, cm_broadcast1, cm_round3, cm_round5, rebuild)

    #verifier check zeta 
    check_zeta(dict_broadcast['round3'])

    #verifier check bigalpha
    check_bigalpha(dict_broadcast['round5'])

    #verifier recompute 
    v_recompute = recompute(circuit, c_info, parties, cm_views, cm_broadcast1, open_views, dict_broadcast['round1'], dict_broadcast['round3'], cm_round3)

    checkrecompute = check_recompute(c_info, parties, dict_broadcast, v_recompute[0], v_recompute[1], v_recompute[2])
    print("passed")






#OLD PROTOCOL
"""
#START COMMENT
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
#END COMMENT

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


#START COMMENT
---check_commitments---
inputs: 
    parties: list of parties opened 
    committed_views: received from prover from round1
    rebuilt_views: rebuild_commitments()[0]
    committed_broadcast: received from prover round 1
    rebuilt_broadcast: rebuild_commitments()[1]
#END COMMENT

def check_commitments(parties, committed_views, rebuilt_views, committed_broadcast, rebuilt_broadcast):
    #check views 
    for i in range(len(parties)):
        assert(rebuilt_views[i] == committed_views[parties[i]]), "Commitment view does not match opened view"

    #check broadcast
    assert (hashlib.sha256(rebuilt_broadcast).hexdigest() == committed_broadcast), "Committed broadcast does not match open broadcast"
    # print("Prover's committed views and broadcast match the opened views and broadcast")
    return 1


"""