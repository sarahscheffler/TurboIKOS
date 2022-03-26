import Fiat_Shamir, tree
from gate import gate
from wire import Wire
import circuit as ct
import Preprocessing as prepro
import Value as v
from Value import Value 
import sys, hashlib
from Cryptodome.Util.number import bytes_to_long, long_to_bytes

def commit(s): 
    return hashlib.sha256(s).hexdigest()

def compute_uncorrupted(n_parties, open_parties):
    party = [p for p in range(n_parties) if p not in open_parties][0]
    return party

def rebuild_wire(c_info, parsed_circuit, e_inputs, e_z, e_z_hat): 
    n_gate, n_wires, n_input, n_parties = c_info['n_gate'], c_info['n_wires'], c_info['n_input'], c_info['n_parties']
    wire_data = [{'e': None, 'v': v.Value() , 'lambda': None, 'lam_hat': {} , 'e_hat': None} for i in range(n_wires)] 
    temp_Wire = Wire(wire_data, 1, n_wires)

    count_mul = 0
    for i in range(n_gate): 
        c = parsed_circuit[i]
        print("TEST C:", c)
        x, y, z = c.x, c.y, c.z 
        if x < n_input: 
            temp_Wire.set_e(x, e_inputs[x])
        if c.operation != "SCA" and y < n_input : 
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
def v_round3(c_info, parsed_circuit, open_parties, v_r1_result, vr1c, broadcast1_open, alpha_m): 
    wire_objects, open_views = v_r1_result[0], v_r1_result[2]
    n_wires, n_gate, n_mul, n_input = c_info['n_wires'], c_info['n_gate'], c_info['n_mul'], c_info['n_input']
    n_parties, n_output = c_info['n_parties'], c_info['n_output']

    r1broadcast_str = vr1c[0] + vr1c[1]
    e_inputs, e_z, e_z_hat =  broadcast1_open['e inputs'], broadcast1_open['e z'], broadcast1_open['e z hat']

    alpha_m_shares = [[Value(0) for x in range(n_parties)] for x in range(n_mul)]
    zeta = [Value(0) for x in range(n_parties)]

    temp_epsilons = Fiat_Shamir.round2(r1broadcast_str, n_mul)
    epsilon1, epsilon2 = temp_epsilons[0], temp_epsilons[1]

    for p in range(len(open_parties)): 
        current_party = open_parties[p]
        party_Wire = wire_objects[p]

        count_mul = 0
        zeta_sum = 0 
        for j in range(len(parsed_circuit)): 
            c = parsed_circuit[j]
            x, y, z = c.x, c.y, c.z
            if c.operation == 'MUL' or c.operation == 'AND': 
                y_lam = party_Wire.lambda_val(y)[0]
                y_lamh = party_Wire.lam_hat(y)[str(count_mul)][0]
                alpha_m_shares[count_mul][current_party] = epsilon1[count_mul]*y_lam + (epsilon2[count_mul]*y_lamh)

                zeta_sum += (epsilon1[count_mul] * party_Wire.e(y) - alpha_m[count_mul])*party_Wire.lambda_val(x)[0] + \
                        epsilon1[count_mul] * party_Wire.e(x) * party_Wire.lambda_val(y)[0] - \
                        epsilon1[count_mul] * party_Wire.lambda_val(z)[0] - epsilon2[count_mul] * party_Wire.lam_hat(z)[str(count_mul)][0]

                if current_party == 0: 
                    zeta_sum += epsilon1[count_mul] * party_Wire.e(z) - epsilon1[count_mul]*party_Wire.e(x)*party_Wire.e(y) + epsilon2[count_mul]*party_Wire.e_hat(z)
            
                count_mul += 1
        if j == len(parsed_circuit)-1:
            zeta[current_party] = zeta_sum

    return alpha_m_shares, zeta

"""
v_r3_result : output from v_round3
"""
def v_compute_r3_commits(c_info, parsed_circuit, v_r3_result, open_parties, alpha_m): 
    n_parties, n_gate = c_info['n_parties'], c_info['n_gate']
    alpha_m_shares, zeta = v_r3_result[0], v_r3_result[1]

    unopened_party = compute_uncorrupted(n_parties, open_parties)

    #compute missing values 
    for i in range(len(alpha_m_shares)): 
        temp_alpha_sum = sum(alpha_m_shares[i])
        missing_alpha = alpha_m[i] - temp_alpha_sum
        alpha_m_shares[i][unopened_party] = missing_alpha

    zeta[unopened_party] = Value(0) - sum(zeta)

    #compute commits
    alpha_m_str = b''
    alpha_m_shares_str = b''
    for gate in range(len(alpha_m_shares)):
        alpha_m_str += long_to_bytes(sum(alpha_m_shares[gate]).value)
        for party in range(len(alpha_m_shares[0])): 
            alpha_m_shares_str += long_to_bytes(alpha_m_shares[gate][party].value)

    zeta_str = b''
    for party in range(n_parties):
        zeta_str += long_to_bytes(zeta[party].value)

    alpha_m_commit = commit(alpha_m_str)
    alpha_m_shares_commit = commit(alpha_m_shares_str)
    zeta_commit = commit(zeta_str)

    return alpha_m_commit, alpha_m_shares_commit, zeta_commit


def check_commits(v_r1_commits_result, v_r3_commits_result, prover_commits): 
    views_commit, broadcast1_commit = v_r1_commits_result[0], v_r1_commits_result[1]
    alpha_m_commit, alpha_m_shares_commit, zeta_commit = v_r3_commits_result[0], v_r3_commits_result[1], v_r3_commits_result[2]

    v_full_commit = commit((views_commit + broadcast1_commit + zeta_commit + alpha_m_commit + alpha_m_shares_commit).encode())

    # print("views commit:", views_commit)
    # print("broadcast1 commit:", broadcast1_commit)
    # print("alpha m commit:", alpha_m_commit)
    # print("alpha m shares commit:", alpha_m_shares_commit)
    # print("zeta commit:", zeta_commit)

    assert(prover_commits == v_full_commit), "Commitments do not match"


def run_verifier(c_info, circuit, run_prover_output, expected_output): 
    # print("---VERIFIER---")

    full_comm, open_broadcast1, alpha_m = run_prover_output[0], run_prover_output[1], run_prover_output[2]
    views_commit, open_path, open_parties = run_prover_output[3], run_prover_output[4], run_prover_output[5]
    hidden_seed = run_prover_output[6]

    e_inputs, e_z, e_z_hat = open_broadcast1['e inputs'], open_broadcast1['e z'], open_broadcast1['e z hat']

    vr1 = v_round1(c_info, circuit, open_parties, open_path, open_broadcast1) # wire_objects, lambda_w, open_views
    wire_objects, lambda_w, open_views = vr1[0], vr1[1], vr1[2]
    vcr1c = v_compute_r1_commits(c_info, circuit, open_parties, hidden_seed, open_views, open_broadcast1, vr1, expected_output) 

    vr3 = v_round3(c_info, circuit, open_parties, vr1, vcr1c, open_broadcast1, alpha_m)
    vcr3c = v_compute_r3_commits(c_info, circuit, vr3, open_parties, alpha_m)

    check_commits(vcr1c, vcr3c, full_comm)


