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
    print( hashlib.sha256(long_to_bytes(r) + v).hexdigest())
    return commit == hashlib.sha256(long_to_bytes(r) + v.encode()).hexdigest()

#inputs: number of parties, number of gates, circuit object, wire object
#output: commited broad cast, broad cast, commit views, views
#output first round    
def round_one(n_parties, n_gate, circuit, wire):
    views_commit = [None]*n_parties
    views = [None]*n_parties
        
    # v output shares
    output_shares = wire.v(circuit[-1].z)
    for j in range(n_parties):
        d = {'input': [], 'input lambda': [], 'lambda z': [], 'lambda y hat': [], 'lambda z hat': []}
        views_str = b''
        for i in range(n_gate):
            g = circuit[i]
            input_str = b''
            input_lam_str = b''
            lam_z_str = b''
            lam_y_hat_str = b''
            lam_z_hat_str = b''
            if g.x < n_input:
                d['input'].append(wire.v(g.x)[j])
                d['input lambda'].append(wire.lambda_val(g.x)[j])
                input_str += long_to_bytes(wire.v(g.x)[j].value)
                input_lam_str += long_to_bytes(wire.lambda_val(g.x)[j].value)
            if g.y < n_input:
                d['input'].append(wire.v(g.y)[j])
                d['input lambda'].append(wire.lambda_val(g.y)[j])
            if g.operation == 'MUL' or 'AND':
                views[j]['lambda z'].append( wire.lambda_val(g.z)[j])
                lam_z_str += long_to_bytes(wire.lambda_val(g.z)[j].value)
                views[j]['lambda y hat'].append(wire.lam_hat(g.y)[j])
                lam_y_hat_str += long_to_bytes(wire.lam_hat(g.y)[j].value)
                views[j]['lambda z hat'].append(wire.lam_hat(g.z)[j])
                lam_z_hat_str += long_to_bytes(wire.lam_hat(g.z)[j].value)
        views[j] = d
        views_str = input_str + input_lam_str + lam_z_str + lam_y_hat_str + lam_z_hat_str
        views_commit[j] = commit(views_str)
            
    return views_commit, views

#input: number of gates, circuit object, wire object, alpha arry arr[#parties][#mulgates], zeta[#parties]
#output: committed broadcast, broadcast
def round_three(n_gate, circuit, wire, alpha, zeta):
    e_inputs = []
    e_input_str = b''
    e_z = []
    e_z_hat = []
    output_shares = []
    output_shares_str = b''
    e_z_str = b''
    e_z_hat_str = b''
    alpha_str = b''
 
    # v output shares
    output_shares = wire.v(circuit[-1].z)
    for j in range(n_parties):
        output_shares_str += long_to_bytes(wire.v(circuit[-1].z).value)
        zeta_str += long_to_bytes(zeta[j].value)

    n_mul = 0
    for i in range(n_gate):
        if i < n_input:
            #e of inputs
            e = wire.e(i)
            e_input_str += long_to_bytes(e.value)
            e_inputs.append(e)
        if circuit[i].operation == 'MUL' or 'AND':
            g = circuit[i]
            #e_z
            val = wire.e(g.z)
            e_z_str += long_to_bytes(val.value)
            e_z.append(val)
            #ez hat
            val = wire.e_hat(g.z)
            e_z_hat_str += long_to_bytes(val.value)e_z_hat.append(val)
            e_z_hat.append(val)
            #alpha
            for j in range(n_parties):
                alpha_str += long_to_bytes(alpha[j][n_mul].value)   

    broadcast = {'e inputs': e_inputs, 'e z': e_z, 'e z hat': e_z_hat, 'alpha': alpha, 'zeta': zeta, 'output shares': output_shares}
    broadcast_str = e_input_str + e_z_str + e_z_hat_str + alpha_str + zeta_str + output_shares_str
    broadcast_commit = commit(broadcast_str)
    return broadcast_commit, broadcast
                                                                                                                                       
    
"""
m wires, n parties

committed broadcast = e input of wire 1 +...+ e input of wire m + e z of wire 1 +...+ e z of wire m + 
                      e z hat share of wire 1 +...+ e z hat share of wire m + alpha party 1 gate 1 + ... + alpha party 1 gate #mul gate +...+
                      alpha party n gate 1 + ... + alpha party n gate #mulgate + zeta party 1 + ... + zeta party n + 
                      output share of party 1 +...+ output share of party n

broadcast = dict{e inputs: arr[m], e z: arr[m], e z hat: arr[m], alpha: arr[n][m], zeta: arr[n], output shares:arr[n]
 
committed views[n] = input of wire 1 + ... input of wire #inputs + lambda of wire 1 + ... + lambda of wire #inputs +
                     lambda z 1 +... + #mult gates lambda z + lambda y hat 1 + ... + #mult gates lambda y hat +
                     lambda y hat 1 + ... + lambda y hat #mult gates

views [n] = dict{input: arr[#inputs], input lambda: arr[#inputs], lambda z: arr[#mult gates], lambda y hat: arr[#mult gates], lambda z hat: arr[#mult gates]}
"""


        
            
if __name__ == '__main__':
    v = 'ziling'
    c = (commit(v.encode()))
    print(open(c[0], v.encode(), c[1]))
  	
