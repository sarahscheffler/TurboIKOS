import sys
import hashlib
from Value import Value
from Cryptodome.Util.number import bytes_to_long, long_to_bytes
from Cryptodome.Cipher import AES
import Fiat_Shamir as fs
import wire, tree
from wire import Wire
from gate import gate
from gmpy2 import mpz
import Preprocessing as prepro
import circuit
import pickle
from serial import *
import prover

"""
commit functions
"""
def commit(s):
    r = Value()
    r.getRand()
    return r.value, hashlib.sha256(long_to_bytes(r.value) + s).hexdigest()

def commit_w_random(s, r): 
    return hashlib.sha256(long_to_bytes(r.value) + s).hexdigest()

def commit_wo_random(s):
    return hashlib.sha256(s).hexdigest()

"""
input: number of wires
output: wire data structure (array of dictionaries with keys 'e', 'v', 'lambda, 'lam_hat', 'e_hat' with index of wire#
"""
def wire_data(n_wires):
    return [{'e': None, 'v': v.Value() , 'lambda': None, 'lam_hat': {} , 'e_hat': None}
                 for i in range(n_wires)]

"""
set inputs to wire object 
"""

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

"""
input: c_info (dictionary of circuit info), parsed_circuit (circuit object), wire (wire object), party_seeds (list of byte strings)
"""
def round1_compute_commits(c_info, parsed_circuit, wire, party_seeds): 
    #TODO come back to about lambda_w
    n_parties, n_gate, n_input = c_info['n_parties'], c_info['n_gate'], c_info['n_input']
    n_wires, n_output = c_info['n_wires'], c_info['n_output']

    #broadcast1 
    e_inputs = []
    e_z = []
    e_z_hat = []
    output_lambda = [] #output_lamda[output wire][party]

    e_inputs_str = b''
    e_z_str = b''
    e_z_hat_str = b''
    output_lambda_str = b''

    #views 
    views_str = ''

    for p in range(n_parties): 
        #views - aka just the seeds 
        views_str += commit_wo_random(party_seeds[p])

    for i in range(n_input): 
        e = wire.e(i)
        e_inputs_str += long_to_bytes(e.value) 
        e_inputs.append(e) 

    for i in range(n_gate):
        g = parsed_circuit[i]
        if g.z >= (n_wires - n_output) and g.z < n_wires:
            lambda_w = wire.lambda_val(g.z)
            output_lambda.append(lambda_w)
            #compute commitment for lambda_w for all output wires 
            for j in lambda_w: 
                output_lambda_str += long_to_bytes(j.value)
        
        #commitments 
        if parsed_circuit[i].operation == 'MUL' or parsed_circuit[i].operation == 'AND':
            #e_z 
            val = wire.e(g.z) 
            e_z.append(val)
            e_z_str += long_to_bytes(val.value)
            #ez hat 
            val = wire.e_hat(g.z)
            e_z_hat.append(val)
            e_z_hat_str += long_to_bytes(val.value)

    broadcast1_open = {'e inputs': e_inputs, 'e z': e_z, 'e z hat': e_z_hat}
    broadcast1_commit = commit_wo_random(e_inputs_str + e_z_str + e_z_hat_str + output_lambda_str)
    views_commit = commit_wo_random(views_str.encode())

    print("output lambda:", output_lambda)

    print("views commit:", views_commit)
    print("broadcast1 commit:", broadcast1_commit)

    return views_commit, broadcast1_commit, party_seeds, broadcast1_open

"""
m wires, n parties 
broadcast1_commit = e input of wire 1 + ... + e input of wire #inputs +
                    e z of wire 1 + ... + e z of wire #mulgates 
                    e z hat of wire 1 + ... + e z hat of wire #mulgates 

broadcast1_open = {'e inputs': arr[#inputs], e z: arr[#mulgates], e z hat: arr[#mulgates]}

views_commit = [party 0 seed, party 1 seed, ..., party n seed]
views_open = arr[n_parties]
"""

"""
open round1
output: views_open, broadcast1_open
"""
def round1_open(r1): 
    return r1[2], r1[3] 

"""
round1 internal 
output: views_commit, broadcast1_commit 
"""
def round1_commits(r1): 
    round1_commit = ''.join(r1[0]) + r1[1]
    return r1[0], r1[1], round1_commit

def compute_alpha(circuit, epsilon_1, epsilon_2, wire, n_gate, n_parties):
    alpha_shares_mulgate = []
    m = 0
    for i in range(n_gate):
        c = circuit[i]
        #MUL gates
        if c.operation == 'MUL' or c.operation == 'AND':
	    # calculate alpha share
            alpha_shares = [None for x in range(n_parties)]
            for j in range(n_parties):
                y_lam = wire.lambda_val(c.y)[j]
                y_lamh = wire.lam_hat(c.y)[str(m)][j]
                # epsilon_1[e][m], y_lam, epsilon_2[e][m], y_lamh (debugging)
                alpha_shares[j] = epsilon_1[m]*y_lam + (epsilon_2[m]*y_lamh)
            alpha_shares_mulgate.append(alpha_shares) #alpha[gate][party]
            m += 1
    #compute single alpha for each mulgate (alpha = epsilon1*lambda_y + epsilon2*lambda_y_hat)
    alpha_broadcast = [None for x in range(len(alpha_shares_mulgate))] #alpha_broadcast[#mul_gate]
    for i in range(len(alpha_shares_mulgate)):
        alpha_broadcast[i] = sum(alpha_shares_mulgate[i])

    return alpha_broadcast, alpha_shares_mulgate

"""
alpha_m_shares = [alpha_m] (refer to paper)
"""
def calculate_beta(c_info, circuit, wire, alpha_m_shares):
    n_parties, n_mul, mult_gates = c_info['n_parties'], c_info['n_mul'], c_info['mult_gates']
    
    beta = [[None*n_parties]*n_parties]
    for i in n_parties: 
        for j in n_parties: 
            temp_sum = Value(0) 
            count_mul = 0
            for m in mult_gates: 
                temp_sum += alpha_m_shares[count_mul][i]*wire.lambda_val(m.x)[j]
                count_mul += 1
            beta[i][j] = temp_sum
            
    return beta

def compute_zeta_share(c_info, circuit, wire, beta, epsilon1, epsilon2): 
    n_parties, mult_gates = c_info['n_parties'], c_info['mult_gates']

    zeta_share = [Value(0) for j in range(n_parties)]

    for j in range(n_parties): 
        temp_sum = Value(0)
        count_mul = 0
        for m in mult_gates: 
            x, y, z = m.x, m.y, m.z
            temp_sum += epsilon1[count_mul] * wire.e(z) - epsilon1[count_mul]*wire.e(y)*wire.e(y) + epsilon2[count_mul]*wire.e_hat(z) + \
                            epsilon1[count_mul]*wire.e(y)*wire.lambda_val(x)[j] + epsilon1[count_mul]*wire.e(x)*wire.lambda_val(y)[j] - \
                                epsilon1[count_mul]*wire.lambda_val(z)[j] - epsilon2[count_mul]*wire.lam_hat(z)[j]

            count_mul += 1
        sum_beta = Value(0)
        for i in n_parties: 
            sum_beta += beta[j][i]

        zeta_share[j] = temp_sum - sum_beta
    
    return zeta_share

def commit_beta_zeta(c_info, beta, zeta_share, seeds): #refer to paper for variables, they match up
    n_parties = c_info['n_parties']

    beta_hashes = []
    capital_H = ''
    for j in n_parties: 
        h_n = b''
        for i in n_parties: 
            h_n += long_to_bytes(beta[i][j])
        temp_random = prepro.generateNum(AES.new(seeds[j], AES.MODE_ECB), 'random', 0)
        h_j = commit_w_random(h_n, temp_random)
        beta_hashes.append(h_j)
        capital_H += h_j
    hat_h = commit_wo_random(capital_H)

    zeta_str = b''
    for z in zeta_share: 
        zeta_str += long_to_bytes(z.value)
    zeta_commit = commit_wo_random(zeta_str)
    
    return hat_h, zeta_commit, beta_hashes

def send_beta(c_info, beta, beta_hashes, uncorrupted_party): 
    n_parties = c_info['n_parties']

    open_beta = [None*n_parties]
    for j in n_parties:
        if j != uncorrupted_party: 
            open_beta[j] = beta[uncorrupted_party][j]
    
    h_i_star = beta_hashes[uncorrupted_party]

    return open_beta, h_i_star

def round3(c_info, circuit, wire, seeds, epsilon1, epsilon2):
    n_gate, n_parties = c_info['n_gate'], c_info['n_parties']
    alpha_m, alpha_m_shares = compute_alpha(circuit, epsilon1, epsilon2, wire, n_gate, n_parties)
    
    beta = calculate_beta(c_info, circuit, wire, alpha_m_shares)
    zeta_share = compute_zeta_share(c_info, circuit, wire, beta, epsilon1, epsilon2)

    r3_commits = commit_beta_zeta(c_info, beta, zeta_share, seeds) #hat_h, zeta_commit, beta_hashes

    return beta, zeta_share, r3_commits

def full_commit(round1_commits, round3_commits): 
    round1_combine = round1_commits[2]
    hat_h, zeta_commit = round3_commits[0], round3_commits[1]
    round3_combine = hat_h + zeta_commit

    full_comm = commit_wo_random((round1_combine + round3_combine).encode())

    return full_comm

def round5(c_info, round1, round3, uncorrupted_party, root, seeds): 
    round1 = round1_open(round1)
    open_broadcast1 = round1[1]

    beta, zeta_share, r3_commits = round3[0], round3[1], round3[2]
    hat_h, zeta_commit, beta_hashes = r3_commits[0], r3_commits[1], r3_commits[2]

    open_path = tree.get_path(uncorrupted_party, root)
    last_hash = commit_wo_random(seeds[uncorrupted_party])
    open_beta, h_i_star = open_beta(c_info, beta, beta_hashes, uncorrupted_party)

    return open_broadcast1, open_path, last_hash, open_beta, h_i_star


def run_prover(c_info, parsed_circuit, wire, n_parties, inputs, party_seeds, root):
    print("---PROVER---")
    n_gate, n_mul = c_info['n_gate'], c_info['n_mul']

    set_inputs(c_info, parsed_circuit, wire, n_parties, inputs)
    
    circuit.compute_output(parsed_circuit, wire, n_gate, n_parties)

    #round1
    r1 = round1_compute_commits(c_info, parsed_circuit, wire, party_seeds)
    r1_commits = round1_commits(r1)
    views_commit, broadcast1_commit, round1_combine = r1_commits[0], r1_commits[1], r1_commits[2]
    r1_open = round1_open(r1)

    #calculate epsilons via Fiat-Shamir transform 
    temp = fs.round2(round1_combine, n_mul)
    epsilon1, epsilon2 = temp[0], temp[1]

    #round 3
    r3 = round3(c_info, circuit, wire, party_seeds, epsilon1, epsilon2)
    r3_commits = r3[2]
    round3_combine = r3_commits[0] + r3_commits[1]
    
    #compute commitment 
    full_com = full_commit(r1_commits, r3_commits)

    #round4
    parties_to_open = fs.round4(round1_combine, round3_combine, n_parties-1, n_parties)
    uncorrupted_party = [p for p in range(n_parties) if p not in parties_to_open][0]

    open_broadcast1, open_path, last_hash, open_beta, h_i_star = round5(c_info, r1, r3, uncorrupted_party, root, party_seeds)

    return full_com, open_broadcast1, open_path, last_hash, open_beta, h_i_star, parties_to_open