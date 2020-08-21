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
    #Parse circuit
    Circuit = circuit.parse(gate)
    n_wires = Circuit[4]
    n_gate = Circuit[3]
    l_input = Circuit[1]
    n_input = Circuit[6]
    n_output = Circuit[5]
    l_output = Circuit[2]
    Circuit = Circuit[0]
    n_parties = 3
    #repeat rep times
    rep = 1000
    #Store each run time in an array
    run_time_arr = [None]*rep
    preprocessing_arr = [None]*rep
    for t in range(rep):
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

        # Create list of wire data    
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

        start_time_preprocessing = time.clock()
        #Assign lambda and lambda hat values
        triples = p.assignLambda(Circuit, w, n_parties)  
        preprocessing_time = time.clock() - start_time_preprocessing
        preprocessing_arr[t] = preprocessing_time

        start_time = time.clock()
        #Calculate alpha shares and write e values, v values, e hat values to output wires 
        alpha = circuit.compute_output(Circuit, epsilon_1, epsilon_2, w, n_gate, n_parties)
        #Compute zeta shares
        zeta = circuit.compute_zeta_share(Circuit, w, alpha, epsilon_1, epsilon_2, n_parties)
       
        run_time = time.clock() - start_time
        run_time_arr[t] = run_time
    
    average_preprocessing_time = sum(preprocessing_arr) / rep
    print('average preprocessing time:', average_preprocessing_time, 'seconds')

    average_run_time = sum(run_time_arr) / rep
    print('average run time:', average_run_time, 'seconds')
    # Proof size = wire size + circuit size + alpha size + zeta size
    #TODO: modify after prover.py and fiatshamir.py with commitment sizes
    proof_size = sys.getsizeof(zeta) + sys.getsizeof(alpha) 
    
    print('proof size:', proof_size)
if __name__ == "__main__": 
    test() 
