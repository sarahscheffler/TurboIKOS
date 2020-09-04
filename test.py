import sys
import random
import circuit 
from gate import gate
from wire import Wire 
import Preprocessing as p
from Value import Value
import prover
import Fiat_Shamir as fs
from Crypto.Util.number import bytes_to_long, long_to_bytes
import verifier as v

def test():
    n_parties = 3
    Circuit = circuit.parse(gate, n_parties)
    n_wires = Circuit[4]
    n_gate = Circuit[3]
    l_input = Circuit[1]
    n_input = Circuit[6]
    n_output = Circuit[5]
    l_output = Circuit[2]
    n_mul = Circuit[8]
    Circuit = Circuit[0]

    # print("input:", n_input)
   
    # Create list of wire data
    
    wire_data = circuit.wire_data(n_wires)
    w = Wire(wire_data, n_parties, n_wires)

    #Preprocessing
    triples = p.assignLambda(Circuit, w, n_parties)

    #Assign v values
    inputs = []
    for i in range(n_input):
        val = Value()
        val.getRand()
        inputs.append(val)
       
    for i in range(n_input):
        w.set_v(i, inputs[i].splitVal(n_parties))
    triples = p.assignLambda(Circuit, w, n_parties)
    #Commit round one
    round1 = prover.round_one_internal(n_parties, n_gate, n_input, Circuit, w)
    views_commit = prover.round_one_external(round1)
    
    #Generate epsilonsir
    r1 = ''.join(views_commit)
    temp = fs.round2(r1, n_mul)
    epsilon_1 = temp[0]
    epsilon_2 = temp[1]
    
    alpha = circuit.compute_output(Circuit, epsilon_1, epsilon_2, w, n_gate, n_parties)
    m = 0
    for i in range(n_gate):
        g = Circuit[i]
        if g.operation == 'AND' or g.operation == 'MUL':
            for j in range(n_parties):
                assert(alpha[m][j] == epsilon_1[m]*w.lambda_val(g.y)[j] + epsilon_2[m]*w.lam_hat(g.y)[j])
            m = m + 1
        
    for j in range(n_gate):
        g = Circuit[j]
        #ADD gate
        if g.operation == 'XOR' or g.operation =='ADD': 
            #Check v 
            assert(sum(w.v(g.z)) == (sum(w.v(g.x)) + sum(w.v(g.y))))
            #Check lambda assignment
            for i in range(n_parties):
                assert(w.lambda_val(Circuit[j].x)[i] + w.lambda_val(Circuit[j].y)[i] == w.lambda_val(Circuit[j].z)[i])
        #MUL gate
        if g.operation == 'AND' or g.operation == 'MUL':
            #Check tripple assignment
            for i in range(n_parties):
                assert(g.a[i] == w.lambda_val(g.x)[i])
                assert(g.b[i] == w.lam_hat(g.y)[i])
                assert(g.c[i] == w.lam_hat(g.z)[i])
            #Check e hat assignment
            assert(w.e_hat(g.z) == sum(w.lambda_val(g.x)) * sum(w.lam_hat(g.y)) + sum(w.lam_hat(g.z)))
            #Chck v value
            assert(sum(w.v(g.z)) == (sum(w.v(g.x)) * sum(w.v(g.y)))) 
    #Check e assignment
    for i in range(n_wires):
        assert(w.e(i) == sum(w.lambda_val(i)) + sum(w.v(i)))

    zeta = circuit.compute_zeta_share(Circuit, w, alpha, epsilon_1, epsilon_2, n_parties)
    #Check zeta
    assert(sum(zeta).value == 0)
    #Commit to broadcast
    round3 = prover.round_three_internal(n_parties, n_gate, n_input, Circuit, w, alpha, zeta)
    broadcast_commit = prover.round_three_external(round3)
    r3 = broadcast_commit
    #number of parties to be corrupted
    t = 2 
    parties = fs.round4(r1, r3, t, n_parties)
    
    #round 5
    temp = prover.round_five(round1, round3, parties)
    r_broadcast = temp[0]
    broadcast = temp[1]
    r_views = temp[2]
    views = temp[3]
    #full_view = viwes of all parties (for debugging)
    full_views = round1[2]
    #r values of all views(for debuggint)
    full_r_views = round1[0]
    #Test prover.py
    #check broadcast and views
    for i in range(n_input):
        assert(w.e(i) == broadcast['e inputs'][i])
        for j in range(n_parties):
            assert(full_views[j]['input'][i] == w.v(i)[j])
            assert(full_views[j]['input lambda'][i] == w.lambda_val(i)[j])
    
    m = 0
    for i in range(n_gate):
        c = Circuit[i]
        if c.operation == 'MUL' or c.operation == 'AND':
            for j in range(n_parties):
                assert(full_views[j]['lambda z'][m] == w.lambda_val(c.z)[j])
                assert(full_views[j]['lambda y hat'][m] == w.lam_hat(c.y)[j])
                assert(full_views[j]['lambda z hat'][m] == w.lam_hat(c.z)[j])
            
            assert(broadcast['e z'][m] == w.e(c.z))
            assert(broadcast['e z hat'][m] == w.e_hat(c.z))
            m += 1

    assert(w.v(Circuit[-1].z) == broadcast['output shares']) 
    
    #check commitment of broadcast
    e_inputs_str = b''
    e_z_str = b''
    e_z_hat_str = b''
    alpha_str = b''
    zeta_str = b''
    output_str = b''
    
    for i in range(n_input):
        e_inputs_str += long_to_bytes(broadcast['e inputs'][i].value)
    for i in range(n_mul):
        e_z_str += long_to_bytes(broadcast['e z'][i].value)
        e_z_hat_str += long_to_bytes(broadcast['e z hat'][i].value)
    for i in range(n_parties):
        for j in range(n_mul):
            alpha_str += long_to_bytes(broadcast['alpha'][j][i].value)
        zeta_str += long_to_bytes(broadcast['zeta'][i].value)
        output_str += long_to_bytes(broadcast['output shares'][i].value)
   
    val = e_inputs_str + e_z_str + e_z_hat_str + alpha_str + zeta_str + output_str
   
    prover.open(r_broadcast, val, broadcast_commit)
    
    #check commitment of views
    for n in range(n_parties):
        input_str = b''
        input_lam_str = b''
        lam_z_str = b''
        lam_y_hat_str = b''
        lam_z_hat_str = b''
        for i in range(n_input):
            input_str += long_to_bytes(full_views[n]['input'][i].value)
            input_lam_str += long_to_bytes(full_views[n]['input lambda'][i].value)
        for i in range(n_mul):
            lam_z_str += long_to_bytes(full_views[n]['lambda z'][i].value)
            lam_y_hat_str += long_to_bytes(full_views[n]['lambda y hat'][i].value)
            lam_z_hat_str += long_to_bytes(full_views[n]['lambda z hat'][i].value)
        val = input_str + input_lam_str + lam_z_str + lam_y_hat_str + lam_z_hat_str
        prover.open(full_r_views[n], val, views_commit[n])




    #verifier test
    
    #check commitments
    #rebuild = v.rebuild_commitments(Circuit, n_input, n_gate, parties, views, r_views, broadcast, r_broadcast)
    #v.check_commitments = v.check_commitments(parties, views_commit, rebuild[0], broadcast_commit, rebuild[1])

    #verifier check zeta 
    #v.check_zeta(broadcast)

    #verifier get epsilon 
    #creater1 = ''.join(views_commit)
    #v_epsilon = v.get_epsilons(creater1.encode(), n_mul)

    #verifier recompute 
    #recompute = v.recompute(Circuit, n_wires, n_gate, n_parties, parties, views, v_epsilon[0], v_epsilon[1], broadcast)
    #checkrecompute = v.check_recompute(parties, n_mul, broadcast, recompute[0], recompute[1], recompute[2])
    
    print('test passed')
if __name__ == "__main__": 
    test() 
