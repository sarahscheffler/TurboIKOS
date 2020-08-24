import sys
import random
import circuit 
from gate import gate
from wire import Wire 
import Preprocessing as p
from Value import Value
import prover

def test():
    Circuit = circuit.parse(gate)
    n_wires = Circuit[4]
    n_gate = Circuit[3]
    l_input = Circuit[1]
    n_input = Circuit[6]
    n_output = Circuit[5]
    l_output = Circuit[2]
    n_mul = Circuit[8]
    Circuit = Circuit[0]
   
    # Create list of wire data
    n_parties = 3    
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
    views = prover.round_one(n_parties, n_gate, n_input, Circuit, w)
    views_commit = views[0]
    views = views[1]
    #Generate epsilons TODO: replace with fiat shamir
    epsilon_1 = Value()
    epsilon_2 = Value()
    epsilon_1.getRand()
    epsilon_2.getRand()
    if n_mul == 1:
        epsilon_1 = [epsilon_1]
        epsilon_2 = [epsilon_2]
    else:
        epsilon_1 = epsilon_1.splitVal(n_mul)
        epsilon_2 = epsilon_2.splitVal(n_mul)

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
    broadcast = prover.round_three(n_parties, n_gate, n_input, Circuit, w, alpha, zeta)
    broadcast_commit = broadcast[0]
    broadcast = broadcast[1]
    print('test passed')
if __name__ == "__main__": 
    test() 
