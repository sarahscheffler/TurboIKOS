import Fiat_Shamir, tree
from gate import gate
from wire import Wire
import circuit as ct
import Preprocessing as prepro
import Value as v
from Value import Value 
import sys, hashlib
from Cryptodome.Util.number import bytes_to_long, long_to_bytes
from Cryptodome.Cipher import AES

def commit(s): 
    return hashlib.sha256(s).hexdigest()

def commit_w_random(s, r): 
    return hashlib.sha256(long_to_bytes(r.value) + s).hexdigest()

def compute_uncorrupted(n_parties, open_parties):
    party = [p for p in range(n_parties) if p not in open_parties][0]
    return party

def rebuild_wire(c_info, parsed_circuit, e_inputs, e_z, e_z_hat): 
    n_gate, n_wires, n_input = c_info['n_gate'], c_info['n_wires'], c_info['n_input']
    wire_data = [{'e': None, 'v': v.Value() , 'lambda': None, 'lam_hat': {} , 'e_hat': None} for i in range(n_wires)] 
    temp_Wire = Wire(wire_data, 1, n_wires)

    count_mul = 0
    for i in range(n_gate): 
        c = parsed_circuit[i]
        x, y, z = c.x, c.y, c.z 
        if x < n_input: 
            temp_Wire.set_e(x, e_inputs[x])
        if y < n_input: 
            temp_Wire.set_e(y, e_inputs[y])
        if c.operation == 'MUL' or c.operation == 'AND': 
            temp_Wire.set_e(z, e_z[count_mul])
            temp_Wire.set_e_hat(z, e_z_hat[count_mul])
            count_mul += 1

    return temp_Wire

def rebuild_inputs(party, wire, n_input):
    for i in range(n_input):
        if party == 0: 
            wire.set_v(i, [wire.e(i) - wire.lambda_val(i)[0]])
        else: 
            wire.set_v(i, [Value(0) - wire.lambda_val(i)[0]])

def get_lambda_w(c_info, parsed_circuit, wire): 
    n_gate, n_wires, n_output = c_info['n_gate'], c_info['n_wires'], c_info['n_output']
    count_output = 0
    lambda_w = [[Value(0) for x in range(n_parties)] for x in range(n_output)] 
    for j in range(n_gate):
        c = parsed_circuit[j]
        z = c.z 
        if z >= n_wires-n_output and z < n_wires: 
            lambda_w[count_output][current_party] = wire.lambda_val(z)[0]
            count_output += 1

    return lambda_w

def v_round1(c_info, v_circuit, open_parties, open_path, open_broadcast1): 
    n_wires, n_gate, n_mul, n_input = c_info['n_wires'], c_info['n_gate'], c_info['n_mul'], c_info['n_input']
    n_parties, n_output = c_info['n_parties'], c_info['n_output']
    e_inputs, e_z, e_z_hat =  open_broadcast1['e inputs'], open_broadcast1['e z'], open_broadcast1['e z hat']

    wire_objects = [None for x in range(len(open_parties))]
    lambda_w = [[Value(0) for x in range(n_parties)] for x in range(n_output)] 
    output_e = []

    open_views = tree.recreate_seeds(open_path)

    for p in range(len(open_parties)): 
        party_Wire = rebuild_wire(c_info, v_circuit, e_inputs, e_z, e_z_hat)

        current_party = open_parties[p]
        seed = open_views[p] 

        rebuild_lam = prepro.rebuildlambda(current_party, seed, v_circuit, party_Wire, c_info)
        rebuild_inputs(current_party, party_Wire, n_input)
        ct.v_compute_output(v_circuit, party_Wire, n_gate, 1)

        count_output = 0 
        for i in range(n_gate): 
            c = v_circuit[i]
            z = c.z 
            if z >= n_wires-n_output and z < n_wires: 
                lambda_w[count_output][current_party] = party_Wire.lambda_val(z)[0]
                count_output += 1
                if p == 0: 
                    output_e.append(party_Wire.e(z))

        wire_objects[p] = party_Wire
        
    return wire_objects, lambda_w, open_views, output_e

"""
uncorrupted_view (hashed seed of uncorrupted view), open_views, open_broadcast1 
"""
"""
uncorrupted_view (hashed seed of uncorrupted view), open_views, open_broadcast1 
"""
def v_compute_r1_commits(c_info, v_circuit, open_parties, uncorrupted_view, open_views, open_broadcast1, v_round1_result, expected_outputs): 
    #---BEGIN FUNCTIONS---#
    def compute_broadcast(e_type): 
        temp_str = b''
        for i in e_type:
            temp_str += long_to_bytes(i.value)
        return temp_str
    #---END FUNCTIONS---#
    n_parties = c_info['n_parties']

    uncorrupted_party = compute_uncorrupted(n_parties, open_parties)
    views_str = ''
    count = 0
    for p in range(n_parties): 
        if p == uncorrupted_party: 
            views_str += uncorrupted_view
            count += 1
        else: 
            views_str += commit(open_views[count])
            count += 1

    e_inputs, e_z, e_z_hat =  open_broadcast1['e inputs'], open_broadcast1['e z'], open_broadcast1['e z hat']
    lambda_w, output_e = v_round1_result[1], v_round1_result[3]

    e_inputs_str = compute_broadcast(e_inputs)
    e_z_str = compute_broadcast(e_z)
    e_z_hat_str = compute_broadcast(e_z_hat)

    for i in range(len(lambda_w)): 
        temp_sum = sum(lambda_w[i])
        missing_lambda_w = output_e[i] - expected_outputs[i] - temp_sum
        lambda_w[i][uncorrupted_party] = missing_lambda_w

    lambda_w_str = b''
    for wire in range(len(lambda_w)): 
        for party in range(len(lambda_w[0])): 
            lambda_w_str += long_to_bytes(lambda_w[wire][party].value)

    views_commit = commit(views_str.encode())

    broadcast1_commit = commit(e_inputs_str + e_z_str + e_z_hat_str + lambda_w_str)

    return views_commit, broadcast1_commit


"""
v_r1_result : output from v_round1
vr1c : output from v_compute_r1_commits
"""
def v_round3(c_info, parsed_circuit, open_parties, v_r1_result, vr1c, broadcast1_open, open_beta): 
    wire_objects, open_views = v_r1_result[0], v_r1_result[2]
    n_wires, n_gate, n_mul, n_input = c_info['n_wires'], c_info['n_gate'], c_info['n_mul'], c_info['n_input']
    n_parties, n_output, mult_gates = c_info['n_parties'], c_info['n_output'], c_info['mult_gates']

    r1broadcast_str = vr1c[0] + vr1c[1]
    e_inputs, e_z, e_z_hat =  broadcast1_open['e inputs'], broadcast1_open['e z'], broadcast1_open['e z hat']

    alpha_m_shares = [[Value(0) for x in range(n_parties)] for x in range(n_mul)] #alpha_m_shares[count_mul][party]
    zeta = [Value(0) for x in range(n_parties)]

    temp_epsilons = Fiat_Shamir.round2(r1broadcast_str, n_mul)
    epsilon1, epsilon2 = temp_epsilons[0], temp_epsilons[1]

    uncorrupted_party = compute_uncorrupted(n_parties, open_parties)

    #compute alpha_m shares
    for p in range(len(open_parties)): 
        current_party = open_parties[p]
        party_Wire = wire_objects[p]

        count_mul = 0
        for j in range(len(parsed_circuit)): 
            m = parsed_circuit[j]
            x, y, z = m.x, m.y, m.z
            if m.operation == 'MUL' or m.operation == 'AND':
                alpha_m_shares[count_mul][current_party] = epsilon1[count_mul]*party_Wire.lambda_val(y)[0] + epsilon2[count_mul]*party_Wire.lam_hat(y)[str(count_mul)][0]
                count_mul += 1

    #compute beta
    beta = [[Value(0) for i in range(n_parties)] for j in range(n_parties)]
    beta[uncorrupted_party] = open_beta
    for i in range(len(open_parties)): 
        i_party = open_parties[i]
        i_wire = wire_objects[i]
        for j in range(len(open_parties)): 
            j_party = open_parties[j]
            j_wire = wire_objects[j]

            temp_sum = Value(0)
            count_mul = 0
            for m in mult_gates: 
                temp_sum += alpha_m_shares[count_mul][i_party] * j_wire.lambda_val(m.x)[0]
                count_mul += 1
            beta[i_party][j_party] = temp_sum

    #compute zeta shares 
    zeta_share = [Value(0) for i in range(n_parties)]
    for j in range(len(open_parties)): 
        current_party = open_parties[j]
        party_Wire = wire_objects[j]

        temp_sum = Value(0)
        count_mul = 0
        for m in mult_gates: 
            x, y, z = m.x, m.y, m.z 
            temp_sum += (epsilon1[count_mul]*party_Wire.e(y)*party_Wire.lambda_val(x)[0]) + (epsilon1[count_mul]*party_Wire.e(x)*party_Wire.lambda_val(y)[0]) - \
                                (epsilon1[count_mul]*party_Wire.lambda_val(z)[0]) - (epsilon2[count_mul]*party_Wire.lam_hat(z)[str(count_mul)][0])
            if current_party == 0: 
                temp_sum += (epsilon1[count_mul] * party_Wire.e(z)) - (epsilon1[count_mul]*party_Wire.e(x)*party_Wire.e(y)) + (epsilon2[count_mul]*party_Wire.e_hat(z))
            count_mul += 1

        sum_beta = Value(0)
        for i in range(n_parties): 
            sum_beta += beta[i][current_party]

        zeta_share[current_party] = temp_sum - sum_beta

    return beta, zeta_share

"""
v_r3_result : output from v_round3
"""
def v_compute_r3_commits(c_info, parsed_circuit, v_r3_result, open_parties, h_i_star, seeds): 
    n_parties = c_info['n_parties']
    beta, zeta_share = v_r3_result[0], v_r3_result[1]

    uncorrupted = compute_uncorrupted(n_parties, open_parties)

    capital_H = ''
    for j in range(n_parties):
        if j == uncorrupted: 
                capital_H += h_i_star
        else: 
            h_n = b''
            for i in range(n_parties): 
                h_n += long_to_bytes(beta[i][j].value)
            temp_random = temp_random = prepro.generateNum(AES.new(seeds[j], AES.MODE_ECB), 'random', 0)
            h_j = commit_w_random(h_n, temp_random)
            capital_H += h_j
    hat_h = commit(capital_H.encode())

    zeta_share[uncorrupted] = Value(0) - sum(zeta_share)
    zeta_str = b''
    for z in zeta_share:
        zeta_str += long_to_bytes(z.value)
    zeta_commit = commit(zeta_str)

    return hat_h, zeta_commit


def check_commits(v_r1_commits_result, v_r3_commits_result, prover_commits): 
    views_commit, broadcast1_commit = v_r1_commits_result[0], v_r1_commits_result[1]
    hat_h, zeta_commit = v_r3_commits_result[0], v_r3_commits_result[1]

    v_full_commit = commit((views_commit + broadcast1_commit + hat_h + zeta_commit).encode())

    # print("views commit:", views_commit)
    # print("broadcast1 commit:", broadcast1_commit)
    # print("hat h:", hat_h)
    # print("zeta commit:", zeta_commit)

    assert(prover_commits == v_full_commit), "Commitments do not match"


def run_verifier(c_info, circuit, run_prover_output, expected_output): 
    # print("---VERIFIER---")

    n_parties = c_info['n_parties']

    full_com, open_broadcast1, open_path = run_prover_output[0], run_prover_output[1], run_prover_output[2]
    hidden_seed, open_beta, h_i_star = run_prover_output[3], run_prover_output[4], run_prover_output[5]
    open_parties = run_prover_output[6]

    e_inputs, e_z, e_z_hat = open_broadcast1['e inputs'], open_broadcast1['e z'], open_broadcast1['e z hat']

    vr1 = v_round1(c_info, circuit, open_parties, open_path, open_broadcast1) # wire_objects, lambda_w, open_views
    wire_objects, lambda_w, open_views = vr1[0], vr1[1], vr1[2]

    count_index = 0
    temp = []
    for i in range(n_parties): 
        if i in open_parties: 
            temp.append(open_views[count_index])
            count_index += 1
        else: 
            temp.append(hidden_seed)

    open_views = temp

    vcr1c = v_compute_r1_commits(c_info, circuit, open_parties, hidden_seed, open_views, open_broadcast1, vr1, expected_output) 

    vr3 = v_round3(c_info, circuit, open_parties, vr1, vcr1c, open_broadcast1, open_beta)
    vcr3c = v_compute_r3_commits(c_info, circuit, vr3, open_parties, h_i_star, open_views)

    check_commits(vcr1c, vcr3c, full_com)


