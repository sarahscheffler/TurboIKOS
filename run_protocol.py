import sys
import random
import circuit 
from gate import gate
from wire import Wire 
from serial import *
import Preprocessing as p
import prover
import Fiat_Shamir as fs
from Value import Value
import time
from objsize import get_deep_size
import unittest
import verifier as v
from Cryptodome.Util.number import bytes_to_long, long_to_bytes
import math
import pickle
import gmpy2

ONE_OUTPUT = False

class TestMPCInTheHead(unittest.TestCase):
    def test_timing_full(self):
        COMMIT_BYTES = 32
        VALUE_BYTES = 8
        SEED_BYTES = int(128/8)
        for test in range(1, len(sys.argv)):
            with self.subTest(test = test):
                #user inputs
                n_parties = int(input('number of parties:'))
                #read in parameter from console and calculate number of repetion
                param = int(input('lambda:'))

                #Calculate repitition
                rep = math.ceil(math.log(0.5**param, 1/n_parties))
                #print("reps: ", rep)

                #Store each run time in an array
                preprocessing_arr = [None]*rep
                run_time_arr = [None]*rep
                verifier_time_arr = [None]*rep
                #initialize size variables
                broadcastc_size = 0
                viewsc_size = 0
                broadcast_size = 0
                views_size_PR = 0

                # n_parties = 3
                temp = circuit.parse(gate, n_parties)
                n_wires = temp[4]
                n_gate = temp[3]
                l_input = temp[1]
                n_input = temp[6]
                n_output = temp[5]
                l_output = temp[2]
                n_mul = temp[8]
                n_sca = temp[-1]
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
                    circuit.compute_output(Circuit, w, n_gate, n_parties)
                    #Commit round one
                    temp = prover.round1(c_info, Circuit, w, party_seeds)
                    # print(temp)
                    # print(pickle.loads(temp)) #PICKLE
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
                    run_time = time.process_time() - start_time
                    run_time_arr[repetition] = run_time

                    #Start time for verifier
                    start_time = time.process_time()

                    #verifier test
                    v.verifier(Circuit, c_info, parties_to_open, views_committed, broadcast1_committed, cm_round3, cm_round5, open_views, dict_rval, dict_broadcast, None)

                    #Set time for verifier
                    verifier_time = time.process_time() - start_time
                    verifier_time_arr[repetition] = verifier_time

                    # print('prover test passed')

                    u_dict_broadcast = deserial(dict_broadcast, c_info)

                    #print(len(u_dict_broadcast))

                    e_inputs = u_dict_broadcast[0]
                    e_z = u_dict_broadcast[1]
                    e_z_hat = u_dict_broadcast[2]
                    output_shares = u_dict_broadcast[3]
                    zeta = u_dict_broadcast[4]
                    little_alpha = u_dict_broadcast[5]
                    alpha = u_dict_broadcast[6]

                    #print(f'len e_inputs: {len(e_inputs)}')
                    #print(f'len e_z: {len(e_z)}')
                    #print(f'len e_z_hat: {len(e_z_hat)}')
                    #print(f'len output_shares: {len(output_shares)}')
                    #print(f'len zeta: {len(zeta)}')
                    #print(f'len little_alpha: {len(little_alpha)}')
                    ##print(f'len big alpha: {len(alpha)}')
                    #print(len(e_inputs) + len(e_z) + len(e_z_hat) + len(output_shares) + len(zeta) + len(little_alpha) + len(alpha))


                    #Calculate size statistics
                    #TODO MANY TEMPORARY HACKS HERE:
                    # NEVER MIND, 8 is BETTER #---# 2. Assume send (big) alpha and zeta in one element---
                    # NEVER MIND, 8 IS BETTER: #---# 4. Already implicitly assuming only one output---
                    # 1. Seed tree instead of sending all N-1 seeds
                    # 3. Assume only one hash instead of one per rep
                        # 7. Overall seed concatenation-commitments can (1) be sent as a single commitment over all repetitions, and (2) be part of an additional commitment
                    # 5. Offset = last party (1/N savings)   (separate optimization section)
                    # 8. Do not need to send Zeta or ouput shares because verifier can recreate and check commitment itself (new and fancy!)

                    if repetition == 0:
                        broadcastc_size += COMMIT_BYTES*3 # send only one hash
                        #viewsc_size += COMMIT_BYTES*len(views_committed)
                    #viewsc_size += COMMIT_BYTES # TEMPORARY SEED TREE HACK
                    # Hack: Okay to just send one commitment to ALL views, we will fill in the blank later
                    #broadcast_size += len(dict_broadcast)
                    broadcast_size += VALUE_BYTES*int(((n_parties-1)/ n_parties)*(len(e_inputs) + len(e_z) + len(e_z_hat))) + VALUE_BYTES*len(little_alpha) # no alpha
                    # 
                    #views_size_PR += SEED_BYTES*len(open_views)
                    views_size_PR += SEED_BYTES*(math.ceil(math.log2(len(open_views))) + 1) # TEMPORARY SEED TREE HACK
                    # print(open_views)


                #Print statistics
                #print('number of parties to corrupt:', n_parties - 1)
                # print('number of add gates:', n_gate-n_mul-n_sca)
                # print('number of mul gates:', n_mul)
                # print('number of sca gates:', n_sca)

                output_wire = [w.v(w.n_wire-1-i) for i in range(n_output)]
                flat_output_wires = serial(output_wire)
                size_output_wires = len(flat_output_wires)

                global ONE_OUTPUT
                if ONE_OUTPUT == False: 
                    proof_size = size_output_wire = broadcastc_size + broadcast_size + viewsc_size + views_size_PR
                else: 
                    proof_size = broadcastc_size + broadcast_size + viewsc_size + views_size_PR

                preprocessing_time = sum(preprocessing_arr)
                #print('preprocessing time:', preprocessing_time, 'seconds')

                run_time = sum(run_time_arr)
                print('run time (seconds):', run_time)
                # Proof size = wire size + circuit size + alpha size + zeta size

                print('broadcast commit size: ', broadcastc_size)
                #print('views commit size: ', viewsc_size) # No more viewsc size, see notes.
                print('broadcast size: ', broadcast_size)
                print('prover views size: ', views_size_PR)
                print('proof size: ', proof_size)
                print('prover time: ', preprocessing_time + run_time)
                print('verifier time: ', sum(verifier_time_arr))
                print('preprocessing time: ', preprocessing_time)

if __name__ == "__main__": 
    unittest.main(argv=[sys.argv[0]])
