"""
test1.py
1) measure run time
2) measure prove size
"""
import sys
import random
import circuit 
from gate import gate
from wire import Wire 
import Preprocessing as p
import prover
import Fiat_Shamir as fs
from Value import Value
import time

def test():
    #Parse circuit
    n_parties = 3
    Circuit = circuit.parse(gate, n_parties)
    n_wires = Circuit[4]
    n_gate = Circuit[3]
    l_input = Circuit[1]
    n_input = Circuit[6]
    n_output = Circuit[5]
    l_output = Circuit[2]
    n_addgate = Circuit[7]
    n_mulgate = Circuit[8]
    Circuit = Circuit[0]

    #repeat rep times
    rep = 1000
    #Store each run time in an array
    run_time_arr = [None]*rep
    preprocessing_arr = [None]*rep
    for t in range(rep):

        # Create list of wire data    
        wire_data = circuit.wire_data(n_wires)
        w = Wire(wire_data, n_parties, n_wires)

        #Timing preprocessing
        start_time_preprocessing = time.process_time()
        triples = p.assignLambda(Circuit, w, n_parties)
        preprocessing_time = time.process_time() - start_time_preprocessing
        preprocessing_arr[t] = preprocessing_time

        #Assign v values
        inputs = []
        for i in range(n_input):
            val = Value()
            val.getRand()
            inputs.append(val)
       
        for i in range(n_input):
            w.set_v(i, inputs[i].splitVal(n_parties))

        start_time_preprocessing = time.process_time()
        triples = p.assignLambda(Circuit, w, n_parties)  
        preprocessing_time = time.process_time() - start_time_preprocessing
        preprocessing_arr[t] = preprocessing_time
        
        #commit round one
        round1 = prover.round_one_internal(n_parties, n_gate, n_input, Circuit, w)
        views_commit = prover.round_one_external(round1)

        #Generate epsilons
        r1 = ''.join(views_commit)
        temp = fs.round2(r1, n_mulgate)
        epsilon_1 = temp[0]
        epsilon_2 = temp[1]

        start_time = time.process_time()
        #Calculate alpha shares and write e values, v values, e hat values to output wires 
        alpha = circuit.compute_output(Circuit, epsilon_1, epsilon_2, w, n_gate, n_parties)
        #Compute zeta shares
        zeta = circuit.compute_zeta_share(Circuit, w, alpha, epsilon_1, epsilon_2, n_parties)
        run_time = time.process_time() - start_time
        run_time_arr[t] = run_time

        #commit broadcast
        round3 = prover.round_three_internal(n_parties, n_gate, n_input, Circuit, w, alpha, zeta)
        broadcast_commit = prover.round_three_external(round3)
        r3 = broadcast_commit
        
        #Generate parties to corrupt
        t = n_parties -1
        parties = fs.round4(r1, r3, t, n_parties)

        #round five
        temp = prover.round_five(round1, round3, parties)
        r_broadcast = temp[0]
        broadcast = temp[1]
        r_views = temp[2]
        views = temp[3]

    print('number of add gates:', n_addgate)
    print('number of mul gates:', n_mulgate)
    average_preprocessing_time = sum(preprocessing_arr) / rep
    print('average preprocessing time:', average_preprocessing_time, 'seconds')

    average_run_time = sum(run_time_arr) / rep
    print('average run time:', average_run_time, 'seconds')
    # Proof size = wire size + circuit size + alpha size + zeta size
    
    proof_size = sys.getsizeof(broadcast_commit) + sys.getsizeof(views_commit) + sys.getsizeof(broadcast) + sys.getsizeof(views)
    print('proof size:', proof_size, 'bytes')
if __name__ == "__main__": 
    test() 
