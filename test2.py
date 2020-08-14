"""
test1.py
1) measure run time
2) measure prove size
"""
import sys
import random
import circuit 
from gate import gate
from gate import Wire 
import Preprocessing as p
from Value import Value
import time

def test():
    #repeat rep times
    rep = 1000
    #Store each run time in an array
    seconds = [None]*1000
    for t in range(rep):
        start_time = time.clock()
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
        #Generate epsilons
        #TODO: replace with fiat shamir
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
        zeta = circuit.compute_zeta_share(Circuit, w, alpha, epsilon_1, epsilon_2, n_parties)
        #Check zeta
        run_time = time.clock() - start_time
        seconds[t] = run_time
    average_time = sum(seconds) / rep
    # Proof size = wire size + circuit size + alpha size + zeta size
    #TODO: modify after prover.py and fiatshamir.py
    proof_size = sys.getsizeof(Circuit) + sys.getsizeof(zeta) + sys.getsizeof(alpha) + sys.getsizeof(w)
    print('average run time:', average_time, 'seconds') 
    print('proof size:', proof_size)
if __name__ == "__main__": 
    test() 
