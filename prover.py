import wire, gate, circuit, tree
import Fiat_Shamir as fs
from Value import Value
import Preprocessing as pre
import hashlib
from Cryptodome.Util.number import bytes_to_long, long_to_bytes
from Cryptodome.Cipher import AES
from serial import *

"""
input: byte string to commit
output: random value in mpz format, commited data in hexadecimal format
commit data 
"""
def commit(s):
    r = Value()
    r.getRand()
    return r.value, hashlib.sha256(long_to_bytes(r.value) + s).hexdigest()

def commit_wo_random(s):
    return hashlib.sha256(s).hexdigest()

"""
input: random value, value, commitment
output: true/false
check if v is correct
"""
def open(r, v, commit):
    return commit == hashlib.sha256(long_to_bytes(r) + v).hexdigest()

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
input: circuit, wire structure, list of n_mul gate alphas, and two epsilons
output: n_parties zeta shares
"""
def compute_zeta_share(circuit, wire, alpha, epsilon_1, epsilon_2, n_parties):
    if alpha == []:
        return []
    r = [None for x in range(n_parties)]
    for i in range(n_parties):
        zeta = 0
        n = 0
        for j in range(len(circuit)):
            if circuit[j].operation == 'AND' or  circuit[j].operation == 'MUL':
                x = circuit[j].x
                y = circuit[j].y
                z = circuit[j].z
                A = sum(alpha[n])
                # epsilon_1[e][n], wire.e(y), A, wire.lambda_val(x)[i], epsilon_1[e][n], wire.e(x), wire.lambda_val(y)[i], epsilon_1[e][n], wire.lambda_val(z)[i], epsilon_2[e][n], wire.lam_hat(z)[str(n)][i]
                zeta += (epsilon_1[n] * wire.e(y) - A)* wire.lambda_val(x)[i] + \
                    epsilon_1[n] * wire.e(x) * wire.lambda_val(y)[i] - \
                    epsilon_1[n] * wire.lambda_val(z)[i] - epsilon_2[n] * wire.lam_hat(z)[str(n)][i]     
                if i == 0:
                    # epsilon_1[e][n], wire.e(z), epsilon_1[e][n], wire.e(x), wire.e(y), epsilon_2[e][n], wire.e_hat(z)
                    zeta += epsilon_1[n] * wire.e(z) - epsilon_1[n]*wire.e(x)*wire.e(y) + epsilon_2[n]*wire.e_hat(z)
                n+= 1   
        if j == len(circuit)-1:
            r[i] = (zeta)

    return r

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
    round1_commit = r1[0] + r1[1]
    return r1[0], r1[1], round1_commit

def round3_compute_commits(c_info, zeta, alpha_broadcast, alpha_shares_mulgate): 
    n_parties, n_mul = c_info['n_parties'], c_info['n_mul']
    
    zeta_str = b''
    alpha_m_str = b''
    alpha_m_shares_str = b''
    
    broadcastr3_open = alpha_broadcast

    for party in range(n_parties): 
        zeta_str += long_to_bytes(zeta[party].value)
    
    for gate_m in range(n_mul): 
        alpha_m_str += long_to_bytes(alpha_broadcast[gate_m].value)
        for party in range(n_parties):
            alpha_m_shares_str += long_to_bytes(alpha_shares_mulgate[gate_m][party].value)

    zeta_commit = commit_wo_random(zeta_str)
    alpha_m_commit = commit_wo_random(alpha_m_str)
    alpha_m_shares_commit = commit_wo_random(alpha_m_shares_str)

    return zeta_commit, alpha_m_commit, alpha_m_shares_commit, broadcastr3_open

"""
zeta_commit = zeta for party 0 + ... + zeta for party n 

alpha_m commit = alpha_m for party 0 + ... + alpha_m for party n 

alpha_m_shares_commit = alpha_m for [gate][party] + ... + alpha_m for [gate][party]
"""

def round3_commits(r3):
    #returns: zeta_commit, alpha_m_commit, alpha_m_shares_commit, round3_combine
    round3_combine = r3[0] + r3[1] + r3[2]
    return r3[0], r3[1], r3[2], round3_combine

def round3_open(r3):
    #returns opened commitments of r3 
    return r3[3] 

def full_commit(round1_commits, round3_commits): 
    views_commit, broadcast1_commit = round1_commits[0], round1_commits[1]
    zeta_commit, alpha_m_commit, alpha_m_shares_commit = round3_commits[0], round3_commits[1], round3_commits[2]

    round1_combine = round1_commits[2]
    round3_combine = round3_commits[3]

    full_commit = commit_wo_random((round1_combine + round3_combine).encode())

    # print("views commit:", views_commit)
    # print("broadcast1 commit:", broadcast1_commit)
    # print("alpha m commit:", alpha_m_commit)
    # print("alpha m shares commit:", alpha_m_shares_commit)
    # print("zeta commit:", zeta_commit)

    return full_commit, views_commit

"""
prover full protocol commit = views_commitment + broadcast1 commitment + zeta commitment + alpha commitment + alpha_m_shares_commitment
"""

"""
input: round1 (output of round1_compute_commits), round3 (output of round3_compute_commits), parties_open (list of parties to open)
"""
def round5(round1, round3, uncorrupted_party, root, seeds): 
    round1, round3 = round1_open(round1), round3_open(round3)
    views, broadcast1, broadcastr3 = round1[0], round1[1], round3

    open_path = tree.get_path(uncorrupted_party, root)
    last_hash = commit_wo_random(seeds[uncorrupted_party])

    #TODO: add serializaton of data 
    return open_path, broadcast1, broadcastr3, last_hash
    

def run_prover(c_info, parsed_circuit, wire, n_parties, inputs, party_seeds, root): 
    # print("---PROVER---") 
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

    #compute alphas
    temp = compute_alpha(parsed_circuit, epsilon1, epsilon2, wire, n_gate, n_parties)
    alpha_public, alpha_private = temp[0], temp[1]

    #compute zetas 
    zeta = compute_zeta_share(parsed_circuit, wire, alpha_private, epsilon1, epsilon2, n_parties)

    #compute round3 
    r3 = round3_compute_commits(c_info, zeta, alpha_public, alpha_private)
    r3_commits = round3_commits(r3)
    round3_combine = r3_commits[3]

    #compute commitment of round1+round3
    temp = full_commit(r1_commits, r3_commits)
    full_comm, views_commit = temp[0], temp[1]

    #round4 - compute corrupted parties via Fiat Shamir Transform 
    parties_to_open = fs.round4(round1_combine, round3_combine, n_parties-1, n_parties)
    uncorrupted_party = [p for p in range(n_parties) if p not in parties_to_open][0]

    #round5 - open broadcasts 
    open_path, open_broadcast1, open_broadcast3, hidden_seed = round5(r1, r3, uncorrupted_party, root, party_seeds)

    return full_comm, open_broadcast1, open_broadcast3, views_commit, open_path, parties_to_open, hidden_seed

