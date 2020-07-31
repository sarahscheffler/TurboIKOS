import sys
import random
import circuit 
from gate import gate
from gate import Wire 
import Preprocessing as p
from Value import Value

def test():
    Circuit = circuit.parse(gate)
    n_wires = Circuit[4]
    n_gate = Circuit[3]
    l_input = Circuit[1]
    n_input = Circuit[6]
    n_output = Circuit[5]
    l_output = Circuit[2]
    Circuit = Circuit[0]
   
    # Create list of wire data
    n_parties = 3    
    wire_data = circuit.wire_data(n_wires)
    w = Wire(wire_data, n_parties, n_wires)
    #Assign v values
    inputs = []
    for i in range(n_input):
        val = Value()
        val.getRand()
        inputs.append(val)
       
    for i in range(n_input):
        w.set_v(i, inputs[i].splitVal(n_parties))
    triples = p.assignLambda(Circuit, w, n_parties)  
    epsilon_1 = Value()
    epsilon_2 = Value()
    epsilon_1.getRand()
    epsilon_2.getRand()
    if n_gate == 1:
        epsilon_1 = [epsilon_1]
        epsilon_2 = [epsilon_2]
    else:
        epsilon_1 = epsilon_1.splitVal(n_gate)
        epsilon_2 = epsilon_2.splitVal(n_gate)
    alpha = circuit.compute_output(Circuit, epsilon_1, epsilon_2, w, n_gate, n_parties)
    
    for j in range(n_gate):
        g = Circuit[j]
        if g.operation == 'XOR' or g.operation =='ADD': 
            assert(sum(w.v(g.z)) == (sum(w.v(g.x)) + sum(w.v(g.y))))
            for i in range(n_parties):
                assert(w.lambda_val(Circuit[j].x)[i] + w.lambda_val(Circuit[j].y)[i] == w.lambda_val(Circuit[j].z)[i])
        if g.operation == 'AND' or g.operation == 'MUL':
            for i in range(n_parties):
                assert(g.a[i] == w.lambda_val(g.x)[i])
                assert(g.b[i] == w.lam_hat(g.y)[i])
                
            assert(sum(g.a)*sum(g.b) == w.e_hat(g.z) - sum(w.lam_hat(g.z)))
            assert(sum(w.v(g.z)) == (sum(w.v(g.x)) * sum(w.v(g.y)))) 
    for i in range(n_wires):
        assert(w.e(i) == sum(w.lambda_val(i)) + sum(w.v(i)))
    zeta = circuit.compute_zeta_share(Circuit, w, alpha, epsilon_1, epsilon_2, n_parties)
    assert(sum(zeta).value == 0)
if __name__ == "__main__": 
    test() 
