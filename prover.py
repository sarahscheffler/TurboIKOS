"""
Commit to views and broadcast
"""

import hashlib
from Value import Value
from Crypto.Util.number import bytes_to_long, long_to_bytes
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

#inputs: number of parties, number of gates, circuit object, wire object
#output: commit views, views
#output first round    
def round_one_internal(n_parties, n_gate, n_input, circuit, wire, party_seeds):
    #one additional argument 
    views_commit = [None]*n_parties
    views = [None]*n_parties
    r = [None]*n_parties
        
    # v output shares
    output_shares = wire.v(circuit[-1].z)
    for j in range(n_parties):
        d = {'input': [], 'party seed': None}
        views_str = b''
        input_str = b''
        seed_str = b''
        d['party seed'] = party_seeds[j]
        seed_str += long_to_bytes(party_seeds[j].value)
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
            
    return r, views_commit, views

#input: number of gates, circuit object, wire object, alpha arry arr[#parties][#mulgates], zeta[#parties]
#output: committed broadcast, broadcast
def round_three_internal(n_parties, n_gate, n_input, circuit, wire, alpha, zeta):
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
    for j in range(n_parties):
        output_shares_str += long_to_bytes(wire.v(circuit[-1].z)[j].value)
        zeta_str += long_to_bytes(zeta[j].value)

    n_mul = 0

    for i in range(n_input):
        #e of inputs
        e = wire.e(i) 
        e_input_str += long_to_bytes(e.value)
        e_inputs.append(e)

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
                alpha_str += long_to_bytes(alpha[n_mul][j].value)   
            n_mul += 1

    broadcast = {'e inputs': e_inputs, 'e z': e_z, 'e z hat': e_z_hat, 'alpha': alpha, 'zeta': zeta, 'output shares': output_shares}
    broadcast_str = e_input_str + e_z_str + e_z_hat_str + alpha_str + zeta_str + output_shares_str
    temp = commit(broadcast_str)
    r = temp[0]
    broadcast_commit = temp[1]
    return r, broadcast_commit, broadcast

#input: output of round_one_internal
#output: committed views
# return round1 to send to verifier/ fiat shamir
def round_one_external(round1):
    return round1[1]

#input: output of round_three_internal
#output: committed broadcast
#return round three to send to verifier/ fiat shamir
def round_three_external(round3):
    return round3[1]

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
