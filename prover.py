"""
Commit to views and broadcast
"""
import wire
import hashlib
from Value import Value
from Cryptodome.Util.number import bytes_to_long, long_to_bytes
import Preprocessing as pre
from Cryptodome.Cipher import AES
import wire

def set_inputs(c_info, circuit, wire, num_parties, real_val):
    n_input = c_info['n_input']

    for i in range(n_input):
        vals = [None]*num_parties
        sum_lambda = sum(wire.lambda_val(i))
        e_val = real_val[i] + sum_lambda
        wire.set_e(i, e_val)
        for j in range(num_parties):
            if j == 0: 
                vals[j] = e_val - wire.lambda_val(i)[j]
            else:
                vals[j] = Value(0)-wire.lambda_val(i)[j]
        wire.set_v(i, vals)
    return


#input: byte string to commit
#output: random value in mpz format, commited data in hexadecimal format
#commit data 
def commit(s):
    r = Value()
    r.getRand()
    return r.value, hashlib.sha256(long_to_bytes(r.value) + s).hexdigest()

#input: random value, value, commitment
#output: true/false
#check if v is correct
def open(r, v, commit):
    return commit == hashlib.sha256(long_to_bytes(r) + v).hexdigest()

#input: c_info (dictionary of circuit info), circuit (circuit object), wire (wire object), party seeds (list of byte strings)
def round1(c_info, circuit, wire, party_seeds): #NEW PROTOCOL 
    n_parties, n_gate, n_input = c_info['n_parties'], c_info['n_gate'], c_info['n_input']
    
    #broadcast1
    e_inputs = []
    e_z = []
    e_z_hat = []
    output_shares = []
    e_inputs_str = b''
    e_z_str = b''
    e_z_hat_str = b''
    output_shares_str = b''

    #views 
    views_commit = [None]*n_parties
    views = [None]*n_parties
    r_views = [None]*n_parties

    output_shares = wire.v(circuit[-1].z)
    for p in range(n_parties):
        #broadcast1 

        output_shares_str += long_to_bytes(output_shares[p].value)

        #views
        # d = {'input': [], 'party seed': None}
        d = party_seeds[p]
        views_str = b''
        input_str = b''
        seed_str = b''
        # d['party seed'] = party_seeds[p]
        seed_str += (party_seeds[p])
        # for i in range(n_input):
        #     d['input'].append(wire.v(i)[p])
        #     input_str += long_to_bytes(wire.v(i)[p].value)
        views[p] = d
        views_str = seed_str
        temp = commit(views_str)
        r_views[p] = temp[0]
        views_commit[p] = temp[1]
    
    #broadcast1 
    for i in range(n_input): 
        e = wire.e(i)
        e_inputs_str += long_to_bytes(e.value)
        e_inputs.append(e)
    
    #broadcast1
    n_mul = 0 
    for i in range(n_gate):
        if circuit[i].operation == 'MUL' or circuit[i].operation == 'AND':
            g = circuit[i]
            #e_z
            val = wire.e(g.z)
            e_z_str += long_to_bytes(val.value)
            e_z.append(val)
            #ez hat
            val = wire.e_hat(g.z)
            e_z_hat_str += long_to_bytes(val.value)
            e_z_hat.append(val)
            n_mul += 1

    broadcast1 = {'e inputs': e_inputs, 'e z': e_z, 'e z hat': e_z_hat, 'output shares': output_shares}
    broadcast1_str = e_inputs_str + e_z_str + e_z_hat_str + output_shares_str
    temp = commit(broadcast1_str)
    r_broadcast1 = temp[0]
    broadcast1_commit = temp[1]

    return views_commit, broadcast1_commit, r_views, r_broadcast1, views, broadcast1

#Internal round1
#output: r views, r broadcast1, views, broadcast1
def round_one_internal(r1):
    return r1[2], r1[3], r1[4], r1[5] 

def round3(c_info, zeta, little_alpha):
    n_parties = c_info['n_parties']
    n_mul = c_info['n_mul']
    zeta_str = b''
    little_alpha_str = b''
    broadcast2 = {'zeta': zeta, 'little_alpha': little_alpha}

    for p in range(n_parties): 
        zeta_str += long_to_bytes(zeta[p].value)
    
    for m in range(n_mul):
        little_alpha_str += long_to_bytes(little_alpha[m].value)

    broadcast2_str = zeta_str + little_alpha_str
    temp = commit(broadcast2_str)
    r_broadcast2 = temp[0]
    broadcast2_commit = temp[1]

    return broadcast2_commit, r_broadcast2, broadcast2

#Return broadcast2 r values and broadcast2
def round_three_internal(r3):
    return r3[1], r3[2]

def round5(c_info,big_alpha): 
    n_parties = c_info['n_parties']
    big_alpha_str = b''

    for p in range(n_parties): 
        big_alpha_str += long_to_bytes(big_alpha[p].value)
    
    temp = commit(big_alpha_str)
    r_broadcast3 = temp[0]
    broadcast3_commit = temp[1]

    return broadcast3_commit, r_broadcast3, big_alpha

#Return broadcast3 r values and broadcast3
def round_five_internal(r5):
    return r5[1], r5[2]

#input: output of round_one_internal
#output: committed views and broadcast1
# return round1 to send to verifier/ fiat shamir
def round_one_external(round1):
    return round1[0], round1[1]

#input: output of round_three_internal
#output: committed broadcast2 (zetas and little alphas)
#return round three to send to verifier/ fiat shamir
def round_three_external(round3):
    return round3[0]

#input: output of round_five_internal 
#output: committed broadcast3 (big alphas)
def round_five_external(round5):
    return round5[0]

"""
input: round1 (output of round_one_internal), round3 (output of round_three_internal), round5 (output of round_five_internal)
        parties_open (list of parties to open)
output: open views, open broadcasts, dictionary of rvals 
"""
def round_seven(round1, round3, round5, parties_open): 
    broadcasts = {'round1': round1[3], 'round3': round3[1], 'round5': round5[1]}
    rval = {'views': round1[0], 'round1': round1[1], 'round3': round3[0], 'round5': round5[0]} #round1, round3, round5 rvals for broadcasts
    views = round1[2]
    r_vals = round1[0]
    open_views = []
    open_rval = []
    for p in parties_open: 
        open_views.append(views[p])
        open_rval.append(r_vals[p])
    rval['views'] = open_rval
    return open_views, rval, broadcasts
                                                                                                                                       
    
"""
m wires, n parties
committed broadcast = e input of wire 1 +...+ e input of wire #inputs + e z of wire 1 +...+ e z of wire #mulgates + 
                      e z hat share of wire 1 +...+ e z hat share of wire #mulgates + alpha party 1 gate 1 + ... + alpha party 1 gate #mul gate +...+
                      alpha party n gate 1 + ... + alpha party n gate #mulgate + zeta party 1 + ... + zeta party n + 
                      output share of party 1 +...+ output share of party n
broadcast = dict{e inputs: arr[#inputs], e z: arr[#mulgates], e z hat: arr[#mulgates], alpha: arr[#mulgates][n], zeta: arr[n], output shares:arr[n]}
 
committed views[n] = input of wire 1 + ... input of wire #inputs + lambda of wire 1 + ... + lambda of wire #inputs +
                     lambda z 1 +... + #mult gates lambda z + lambda y hat 1 + ... + #mult gates lambda y hat +
                     lambda y hat 1 + ... + lambda y hat #mult gates + lambda z hat 1  +... lambda z hat #mulgates
views [n] = dict{input: arr[#inputs], input lambda: arr[#inputs], lambda z: arr[#mult gates], lambda y hat: arr[#mult gates], lambda z hat: arr[#mult gates]}
"""






#OLD PROTOCOL 
"""
#inputs: number of parties, number of gates, circuit object, wire object
#output: commit views, views
#output first round    
def round_one_internal_old(n_parties, n_gate, n_input, circuit, wire, party_seeds):
    #one additional argument 
    views_commit = [None]*n_parties
    views = [None]*n_parties
    r = [None]*n_parties
        
    # v output shares
    # output_shares = wire.v(circuit[-1].z)
    for j in range(n_parties):
        d = {'input': [], 'party seed': None}
        views_str = b''
        input_str = b''
        seed_str = b''
        d['party seed'] = party_seeds[j]
        seed_str += (party_seeds[j])
        for i in range(n_input):
            d['input'].append(wire.v(i)[j])
            # d['party seed'].append(party_seeds[j])
            input_str += long_to_bytes(wire.v(i)[j].value)
            # seed_str += long_to_bytes(party_seeds[j].value)
        # for i in range(n_gate):
        #     g = circuit[i]
        #     if g.operation == 'MUL' or g.operation == 'AND':
        #         d['party seed'].append(party_seeds[j])
        #         seed_str += long_to_bytes(party_seeds[j].value)
        views[j] = d
        views_str = input_str + seed_str
        temp = commit(views_str)
        r[j] = temp[0]
        views_commit[j] = temp[1]
            
    return r, views_commit, views"""

"""
#input: number of gates, circuit object, wire object, alpha arry arr[#parties][#mulgates], zeta[#parties]
#output: committed broadcast, broadcast
def round_three_internal(n_parties, n_gate, n_input, n_epsilons, circuit, wire, alpha, zeta):
    e_inputs = []
    e_input_str = b''
    e_z = []
    e_z_hat = []
    output_shares = []
    output_shares_str = b''
    e_z_str = b''
    e_z_hat_str = b''
    alpha_str = b''
    zeta_str = b''

    # v output shares
    output_shares = wire.v(circuit[-1].z)
    for e in range(n_epsilons):     
        for j in range(n_parties):
            if e == 0:
                output_shares_str += long_to_bytes(wire.v(circuit[-1].z)[j].value)

            zeta_str += long_to_bytes(zeta[e][j].value)

    for i in range(n_input):
        #e of inputs
        e = wire.e(i) 
        e_input_str += long_to_bytes(e.value)
        e_inputs.append(e)
    
    for e in range(n_epsilons):
        n_mul = 0
        for i in range(n_gate):
            if circuit[i].operation == 'MUL' or circuit[i].operation == 'AND':
                g = circuit[i]
                #e_z
                val = wire.e(g.z)
                e_z_str += long_to_bytes(val.value)
                e_z.append(val)
                #ez hat
                val = wire.e_hat(g.z)
                e_z_hat_str += long_to_bytes(val.value)
                e_z_hat.append(val)
                #alpha
                for j in range(n_parties):
                    alpha_str += long_to_bytes(alpha[n_mul][e][j].value)   
                n_mul += 1
    broadcast = {'e inputs': e_inputs, 'e z': e_z, 'e z hat': e_z_hat, 'alpha': alpha, 'zeta': zeta, 'output shares': output_shares}
    broadcast_str = e_input_str + e_z_str + e_z_hat_str + alpha_str + zeta_str + output_shares_str
    temp = commit(broadcast_str)
    r = temp[0]
    broadcast_commit = temp[1]
    return r, broadcast_commit, broadcast
    """

"""
#input: output of round_one_internal, output of round_three_internal, list of parties to open
#output: r of broadcast, broadcast, chosen r values of views, chosen views
#generate round five
def round_five(round1, round3, parties):
    v = []
    r = []
    views = round1[2]
    r_views = round1[0]
    for i in parties:
        v.append(views[i])
        r.append(r_views[i])
    return round3[0], round3[2], r, v
"""