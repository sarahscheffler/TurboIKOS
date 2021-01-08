'''
run full protocol of prover code
'''
import circuit
from gate import gate
from wire import Wire
import Preprocessing as p
from Value import Value
import prover
import Fiat_Shamir as fs
import time
# from objsize import get_deep_size
# from pympler import asizeof
# import resource
import os
import psutil
import verifier as v
from Cryptodome.Util.number import bytes_to_long, long_to_bytes
import math

COMMIT_BYTES = 32
VALUE_BYTES = 16
SEED_BYTES = int(256/8)

def get_process_memory():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss

            
def benchmarking(n_parties):

    #read in parameter from console and calculate number of repition
    param = 80

    #Calculate repitition
    rep = math.ceil(math.log(0.5**param, 1/n_parties))

    #Store each run time in an array
    preprocessing_arr = [None]*rep
    prover_time_arr = [None]*rep
    verifier_time_arr = [None]*rep
    #initialize size variables
    broadcastc_size = 0
    viewsc_size = 0
    broadcast_size = 0
    views_size_PR = 0
    proof_size = 0
    memory = 0

    temp = circuit.parse(gate, n_parties)
    n_wires = temp[4]
    n_gate = temp[3]
    l_input = temp[1]
    n_input = temp[6]
    n_output = temp[5]
    l_output = temp[2]
    n_mul = temp[8]
    c_info = temp[10]
    Circuit = temp[0]
      
    for repetition in range(rep): 
        # Create list of wire data
        wire_data = circuit.wire_data(n_wires)
        w = Wire(wire_data, n_parties, n_wires)

        #Timing preprocessing
        start_time_preprocessing = time.process_time()

        #Preprocessing - assign lambdas and triples, generate master seeds 
        assign_lambda = p.PRassignLambda(Circuit, w, n_parties)
        triples = assign_lambda[0]
        party_seeds = assign_lambda[1]

        #Assign v values
        inputs = []
        for i in range(n_input):
            val = Value()
            val.getRand()
            inputs.append(val)
                
        prover.set_inputs(c_info, Circuit, w, n_parties, inputs)
        # for i in range(n_input):
        #     w.set_v(i, inputs[i].splitVal(n_parties))
        # triples = p.assignLambda(Circuit, w, n_parties)
        circuit.compute_output(Circuit, w, n_gate, n_parties)
        #Commit round one
        temp = prover.round1(c_info, Circuit, w, party_seeds)
        r1 = prover.round_one_external(temp)
        views_committed = r1[0]
        broadcast1_committed = r1[1]
        round1_internal = prover.round_one_internal(temp)

        #Get preprocessing time
        preprocessing_time = time.process_time() - start_time_preprocessing
        preprocessing_arr[repetition] = preprocessing_time

        #Generate epsilons
        cm_round1 = ''.join(views_committed) + broadcast1_committed
        temp = fs.round2(cm_round1, n_mul)
        epsilon_1 = temp[0]
        epsilon_2 = temp[1]

        start_time = time.process_time()
        start_memory = get_process_memory()
        #Compute alphas
        temp = circuit.compute_alpha(Circuit, epsilon_1, epsilon_2, w, n_gate, n_parties)
        #alphas to broadcast
        alpha_public = temp[0]
        #alphas shares for each party (secret)
        alpha_private = temp[1]

        zeta = circuit.compute_zeta_share(Circuit, w, alpha_private, epsilon_1, epsilon_2, n_parties)

        #Round3 commit
        temp = prover.round3(c_info, zeta, alpha_public)
        cm_round3 = prover.round_three_external(temp)
        round3_internal = prover.round_three_internal(temp)
                    
        #Round 4
        temp = fs.round_4(cm_round3, n_mul)
        gamma1 = temp[0]
        gamma2 = temp[1]
                
        #round 5 
        A = circuit.compute_A_share(alpha_public, alpha_private, gamma1, n_parties)
        round5 = prover.round5(c_info, A)
        cm_round5 = prover.round_five_external(round5)
        round5_internal = prover.round_five_internal(round5)
                
        #round 6
        T = n_parties -1 
        parties_to_open = fs.round6(cm_round1, cm_round3, T, n_parties)

        #round7
        r7 = prover.round_seven(round1_internal, round3_internal, round5_internal, parties_to_open)
        open_views = r7[0]
        dict_rval = r7[1]
        dict_broadcast = r7[2]

        #Set run time
        prover_time = time.process_time() - start_time
        prover_time_arr[repetition] = prover_time

        #Calculate size statistics
        broadcastc_size += COMMIT_BYTES
        viewsc_size += COMMIT_BYTES*n_parties
        # broadcast_size += sum([sum([sum([VALUE_BYTES for v in dict_broadcast[broadcast][i]]) for i in dict_broadcast[broadcast]]) for broadcast in dict_broadcast  if (broadcast!= "round5")]) + sum([VALUE_BYTES for v in dict_broadcast["round5"]])
        broadcast_size += VALUE_BYTES*n_input + VALUE_BYTES*3*n_mul + VALUE_BYTES*2*n_parties + VALUE_BYTES*n_output
        views_size_PR += SEED_BYTES*n_parties
        # memory = max(memory,get_process_memory() - start_memory)
        memory = get_process_memory()

        #Start time for verifier
        start_time = time.process_time()

        #verifier test
        v.verifier(Circuit, c_info, parties_to_open, views_committed, broadcast1_committed, cm_round3, cm_round5, open_views, dict_rval, dict_broadcast)

        #Set time for verifier
        verifier_time = time.process_time() - start_time
        verifier_time_arr[repetition] = verifier_time

        # memory += sys.getsizeof(broadcastc_size) + sys.getsizeof(viewsc_size) + sys.getsizeof(broadcast_size) + sys.getsizeof(views_size_PR)
        # memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        proof_size += broadcastc_size + viewsc_size + broadcast_size + views_size_PR
        
    # preprocessing_time = sum(preprocessing_arr)
    # print('preprocessing time:', preprocessing_time, 'seconds')

    prover_time_total = sum(prover_time_arr)
    verifier_time_total = sum(verifier_time_arr)
    # Proof size = wire size + circuit size + alpha size + zeta size

    return prover_time_total, verifier_time_total, proof_size, memory, rep

