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
from objsize import get_deep_size
import math

def test():
    #Parse circuit
    n_parties = int(input('number of parties:'))
    #read in parameter from console and calculate number of repition
    param = int(input('lambda:'))
    repetition = math.ceil(math.log(0.5**param, 1/n_parties))
    Circuit = circuit.parse(gate, n_parties)
    n_wires = Circuit[4]
    n_gate = Circuit[3]
    l_input = Circuit[1]
    n_input = Circuit[6]
    n_output = Circuit[5]
    l_output = Circuit[2]
    n_addgate = Circuit[7]
    n_mulgate = Circuit[8]
    c_info = Circuit[10]
    Circuit = Circuit[0]

    #repeat rep timesssign input values
    inputs = []
    for i in range(n_input):
        val = Value()
        val.getRand()
        inputs.append(val)
    
    rep = 1
    #Store each run time in an array
    run_time_arr = [0]*rep
    preprocessing_arr = [0]*rep
    for t in range(rep):

        for z in range(repetition):

            # Create list of wire data    
            wire_data = circuit.wire_data(n_wires)
            w = Wire(wire_data, n_parties, n_wires)
            #Timing preprocessing
            start_time_preprocessing = time.process_time()
            triples = p.assignLambda(Circuit, w, n_parties)
            preprocessing_time = time.process_time() - start_time_preprocessing
            preprocessing_arr[t] += preprocessing_time
           
            for i in range(n_input):
                w.set_v(i, inputs[i].splitVal(n_parties))

            start_time_preprocessing = time.process_time()
            #Preprocessing - assign lambdas and triples, generate master seeds 
            assign_lambda = p.PRassignLambda(Circuit, w, n_parties)
            triples = assign_lambda[0]
            party_seeds = assign_lambda[1]
            
            #commit round one
            round1 = prover.round_one_internal(n_parties, n_gate, n_input, Circuit, w, party_seeds)
            views_commit = prover.round_one_external(round1)
            preprocessing_time = time.process_time() - start_time_preprocessing
            preprocessing_arr[t] += preprocessing_time
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
            
            #commit broadcast
            round3 = prover.round_three_internal(n_parties, n_gate, n_input, Circuit, w, alpha, zeta)
            broadcast_commit = prover.round_three_external(round3)
            r3 = broadcast_commit
            run_time = time.process_time() - start_time
            run_time_arr[t] += run_time
            
            #Generate parties to corrupt
            n_corrupt = n_parties -1
            parties = fs.round4(r1, r3, n_corrupt, n_parties)

            #round five
            temp = prover.round_five(round1, round3, parties)
            r_broadcast = temp[0]
            broadcast = temp[1]
            r_views = temp[2]
            views = temp[3]

    print('number of parties to corrupt:', n_corrupt)
    print('number of add gates:', n_addgate)
    print('number of mul gates:', n_mulgate)
    average_preprocessing_time = sum(preprocessing_arr) / rep
    print('average preprocessing time:', average_preprocessing_time, 'seconds')

    average_run_time = sum(run_time_arr) / rep
    print('average run time:', average_run_time, 'seconds')
    # Proof size = wire size + circuit size + alpha size + zeta size
    
    COMMIT_BYTES = 32
    VALUE_BYTES = 16
    SEED_BYTES = int(256/8)
    broadcastc_size = rep*COMMIT_BYTES
    viewsc_size = rep*COMMIT_BYTES*len(views_commit)
    broadcast_size = rep*(sum([sum([VALUE_BYTES for v in broadcast[k]]) for k in broadcast if k!= "alpha"]) + sum([VALUE_BYTES for v in broadcast["alpha"][i] for i in range(n_mulgate)]))
    print("TODO: Will need to make 'output shares' also a 2D array")
    views_size = rep*sum([sum([sum([VALUE_BYTES for v in views[i][k]]) for k in views[i]]) for i in range(t)])
    views_size_PR = rep*(sum([sum([VALUE_BYTES for v in views[i]["input"]]) for i in range(t)]) + SEED_BYTES*t)
    print("TODO: views_size will get much smaller when pseudorandom lambdas are introduced")
    proof_size = broadcastc_size + viewsc_size + broadcast_size + views_size
    print('proof size:', proof_size, 'bytes')
    print('broadcast commit size:', broadcastc_size)
    print('views commit size:', viewsc_size)
    print('broadcast size:', broadcast_size)
    print('views size:', views_size)
    print("---(TODO)---")
    print('proof size (pseudorandom):', broadcastc_size + viewsc_size + broadcast_size + views_size_PR, 'bytes')
    print('views size (pseudorandom):', views_size_PR, 'bytes')
    COMMIT_BYTES = 32
    VALUE_BYTES = 16
    SEED_BYTES = int(256/8)
    broadcastc_size = rep*COMMIT_BYTES
    viewsc_size = rep*COMMIT_BYTES*len(views_commit)
    broadcast_size = rep*(sum([sum([VALUE_BYTES for v in broadcast[k]]) for k in broadcast if k!= "alpha"]) + sum([VALUE_BYTES for v in broadcast["alpha"][i] for i in range(n_mulgate)]))
    print("TODO: Will need to make 'output shares' also a 2D array")
    views_size = rep*sum([sum([sum([VALUE_BYTES for v in views[i][k]]) for k in views[i]]) for i in range(t)])
    views_size_PR = rep*(sum([sum([VALUE_BYTES for v in views[i]["input"]]) for i in range(t)]) + SEED_BYTES*t)
    print("TODO: views_size will get much smaller when pseudorandom lambdas are introduced")
    proof_size = broadcastc_size + viewsc_size + broadcast_size + views_size
    print('proof size:', proof_size, 'bytes')
    print('broadcast commit size:', broadcastc_size)
    print('views commit size:', viewsc_size)
    print('broadcast size:', broadcast_size)
    print('views size:', views_size)
    print("---(TODO)---")
    print('proof size (pseudorandom):', broadcastc_size + viewsc_size + broadcast_size + views_size_PR, 'bytes')
    print('views size (pseudorandom):', views_size_PR, 'bytes')
                                                                                            
if __name__ == "__main__": 
    test() 