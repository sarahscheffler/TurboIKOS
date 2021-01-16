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
import unittest
import verifier as v
from Cryptodome.Util.number import bytes_to_long, long_to_bytes
import math

class TestMPCInTheHead(unittest.TestCase):
    def test_seed(self):
        for test in range(1, len(sys.argv)):
            with self.subTest(test = test):
                n_parties = 3
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

                # Create list of wire data
                n_parties = 3    
                wire_data = circuit.wire_data(n_wires)
                w = Wire(wire_data, n_parties, n_wires)

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
                r1 = prover.round_one_external(temp)
                views_committed = r1[0]
                broadcast1_committed = r1[1]
                round1_internal = prover.round_one_internal(temp)
                #Generate epsilons
                cm_round1 = ''.join(views_committed) + broadcast1_committed
                temp = fs.round2(cm_round1, n_mul)
                epsilon_1 = temp[0]
                epsilon_2 = temp[1]

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
                T = 2
                parties_to_open = fs.round6(cm_round1, cm_round3, T, n_parties)

                #round7
                r7 = prover.round_seven(round1_internal, round3_internal, round5_internal, parties_to_open)
                open_views = r7[0]
                dict_rval = r7[1]
                dict_broadcast = r7[2]

                #verifier test
                v.verifier(Circuit, c_info, parties_to_open, views_committed, broadcast1_committed, cm_round3, cm_round5, open_views, dict_rval, dict_broadcast)
                print('prover test passed')
    
    
    def test_timing_full(self):
        COMMIT_BYTES = 32
        VALUE_BYTES = 16
        SEED_BYTES = int(256/8)
        for test in range(1, len(sys.argv)):
            with self.subTest(test = test):
                #user inputs
                n_parties = int(input('number of parties:'))
                #read in parameter from console and calculate number of repition
                param = int(input('lambda:'))

                #Calculate repitition
                rep = math.ceil(math.log(0.5**param, 1/n_parties))

                #Store each run time in an array
                preprocessing_arr = [None]*rep
                run_time_arr = [None]*rep
                verifier_time_arr = [None]*rep
                #initialize size variables
                broadcastc_size = 0
                viewsc_size = 0
                broadcast_size = 0
                views_size_PR = 0

                n_parties = 3
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
                    v.verifier(Circuit, c_info, parties_to_open, views_committed, broadcast1_committed, cm_round3, cm_round5, open_views, dict_rval, dict_broadcast)

                    #Set time for verifier
                    verifier_time = time.process_time() - start_time
                    verifier_time_arr[repetition] = verifier_time

                    print('prover test passed')

                    #Calculate size statistics
                    broadcastc_size += COMMIT_BYTES*3
                    viewsc_size += COMMIT_BYTES*len(views_committed)
                    broadcast_size += sum([sum([sum([VALUE_BYTES for v in dict_broadcast[broadcast][i]]) for i in dict_broadcast[broadcast]]) for broadcast in dict_broadcast  if (broadcast!= "round5")]) + sum([VALUE_BYTES for v in dict_broadcast["round5"]])
                    views_size_PR += sum([sum([VALUE_BYTES for v in  open_views[i]]) for i in range(n_parties-1)]) + SEED_BYTES*(n_parties-1)


                #Print statistics
                print('number of parties to corrupt:', n_parties - 1)
                print('number of add gates:', n_gate-n_mul)
                print('number of mul gates:', n_mul)

                preprocessing_time = sum(preprocessing_arr)
                print('preprocessing time:', preprocessing_time, 'seconds')

                run_time = sum(run_time_arr)
                print('run time:', run_time, 'seconds')
                # Proof size = wire size + circuit size + alpha size + zeta size

                print('broadcast commit size:', broadcastc_size)
                print('views commit size:', viewsc_size)
                print('broadcast size:', broadcast_size)
                print('prover views size:', views_size_PR)
    
if __name__ == "__main__": 
    unittest.main(argv=[sys.argv[0]])