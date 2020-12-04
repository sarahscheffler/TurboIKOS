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
from circuit import n_epsilons
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
               
                for i in range(n_input):
                    w.set_v(i, inputs[i].splitVal(n_parties))
                # triples = p.assignLambda(Circuit, w, n_parties)
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
               
                for i in range(n_input):
                    w.set_v(i, inputs[i].splitVal(n_parties))
                # triples = p.assignLambda(Circuit, w, n_parties)
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
    
    # def test_timing_full(self):
    #     COMMIT_BYTES = 32
    #     VALUE_BYTES = 16
    #     SEED_BYTES = int(256/8)
    #     for test in range(1, len(sys.argv)):
    #         with self.subTest(test = test):
    #             #Parse circuit
    #             n_parties = 3    
    #             Circuit = circuit.parse(gate, n_parties)
    #             n_wires = Circuit[4]
    #             n_gate = Circuit[3]
    #             l_input = Circuit[1]
    #             n_input = Circuit[6]
    #             n_output = Circuit[5]
    #             l_output = Circuit[2]
    #             n_mulgate = Circuit[8]
    #             n_parties = Circuit[9]
    #             c_info = Circuit[10]
    #             Circuit = Circuit[0]

    #             #repeat rep times
    #             rep = 1
    #             #Store each run time in an array
    #             preprocessing_arr = [None]*rep
    #             run_time_arr = [None]*rep
    #             verifier_time_arr = [None]*rep
    #             for repetition in range(rep):
    #                 broadcastc_size = 0
    #                 viewsc_size = 0
    #                 broadcast_size = 0
    #                 views_size_PR = 0

    #                 # Create list of wire data    
    #                 wire_data = circuit.wire_data(n_wires)
    #                 w = Wire(wire_data, n_parties, n_wires)

    #                 #Timing preprocessing
    #                 start_time_preprocessing = time.process_time()

    #                 #Preprocessing - assign lambdas and triples, generate master seeds 
    #                 assign_lambda = p.PRassignLambda(Circuit, w, n_parties)
    #                 triples = assign_lambda[0]
    #                 party_seeds = assign_lambda[1]

    #                 preprocessing_time = time.process_time() - start_time_preprocessing
    #                 preprocessing_arr[repetition] = preprocessing_time

    #                 #Assign v values
    #                 inputs = []
    #                 for i in range(n_input):
    #                     val = Value()
    #                     val.getRand()
    #                     inputs.append(val)
                                       
    #                 for i in range(n_input):
    #                     w.set_v(i, inputs[i].splitVal(n_parties))

    #                 start_time_preprocessing = time.process_time()
                    
    #                 #commit round one
    #                 round1 = prover.round_one_internal(n_parties, n_gate, n_input, Circuit, w, party_seeds)
    #                 views_commit = prover.round_one_external(round1)

    #                 #TODO: Why is preprocessing_time set twice?
    #                 preprocessing_time = time.process_time() - start_time_preprocessing
    #                 preprocessing_arr[repetition] = preprocessing_time

    #                 #Generate epsilons
    #                 r1 = ''.join(views_commit)
    #                 temp = fs.round2(r1, n_mulgate, n_epsilons)
    #                 epsilon_1 = temp[0]
    #                 epsilon_2 = temp[1]

    #                 start_time = time.process_time()
    #                 #Calculate alpha shares and write e values, v values, e hat values to output wires 
    #                 alpha = circuit.compute_output(Circuit, epsilon_1, epsilon_2, w, n_gate, n_parties, n_epsilons)
    #                 #Compute zeta shares
    #                 zeta = circuit.compute_zeta_share(Circuit, w, alpha, epsilon_1, epsilon_2, n_parties, n_epsilons)
                    
    #                 #commit broadcast
    #                 round3 = prover.round_three_internal(n_parties, n_gate, n_input, n_epsilons, Circuit, w, alpha, zeta)
    #                 broadcast_commit = prover.round_three_external(round3)
    #                 r3 = broadcast_commit
    #                 run_time = time.process_time() - start_time
    #                 run_time_arr[repetition] = run_time
                    
    #                 #Generate parties to corrupt
    #                 t = n_parties -1
    #                 parties = fs.round4(r1, r3, t, n_parties)

    #                 #round five
    #                 temp = prover.round_five(round1, round3, parties)
    #                 r_broadcast = temp[0]
    #                 broadcast = temp[1]
    #                 r_views = temp[2]
    #                 views = temp[3]

    #                 start_time = time.process_time()
    #                 v.verifier(Circuit, c_info, n_parties, parties, views_commit, views, r_views, broadcast_commit, broadcast, r_broadcast, n_epsilons)
    #                 verifier_time = time.process_time() - start_time
    #                 verifier_time_arr[repetition] = verifier_time

    #                 broadcastc_size += COMMIT_BYTES
    #                 viewsc_size += COMMIT_BYTES*len(views_commit)
    #                 broadcast_size += sum([sum([VALUE_BYTES for v in broadcast[k]]) for k in broadcast if (k!= "alpha" or k!= "zeta")])+sum([VALUE_BYTES for v in broadcast["alpha"] for i in range(n_parties)])*n_epsilons + sum([VALUE_BYTES for v in broadcast["zeta"][0] for i in range(n_parties)])*n_epsilons
    #                 views_size_PR += sum([sum([VALUE_BYTES for v in views[i]["input"]]) for i in range(t)]) + SEED_BYTES*t

    #             print('number of gates:', n_gate)
    #             print('number of add gates:', n_gate - n_mulgate)
    #             print('number of mul gates:', n_mulgate)
    #             preprocessing_time = sum(preprocessing_arr) 
    #             print('preprocessing time:', preprocessing_time, 'seconds')

    #             run_time = sum(run_time_arr) 
    #             print('run time:', run_time, 'seconds')
    #             # Proof size = wire size + circuit size + alpha size + zeta size
                
                

    #             print('broadcast commit size:', broadcastc_size)
    #             print('views commit size:', viewsc_size)
    #             print('broadcast size:', broadcast_size)
    #             print('prover views size:', views_size_PR)
    #             print('timing test passed')
                
    # def test_repeat(self):
    #     COMMIT_BYTES = 32
    #     VALUE_BYTES = 16
    #     SEED_BYTES = int(256/8) #16??
    #     for test in range(1, len(sys.argv)):
    #         with self.subTest(test = test):
    #             #Parse circuit
    #             n_parties = int(input('number of parties:'))
    #             #read in parameter from console and calculate number of repition
    #             param = int(input('lambda:'))
    #             rep = math.ceil(math.log(0.5**param, 1/n_parties))
    #             Circuit = circuit.parse(gate, n_parties)
    #             n_wires = Circuit[4]
    #             n_gate = Circuit[3]
    #             l_input = Circuit[1]
    #             n_input = Circuit[6]
    #             n_output = Circuit[5]
    #             l_output = Circuit[2]
    #             n_addgate = Circuit[7]
    #             n_mulgate = Circuit[8]
    #             c_info = Circuit[10]
    #             Circuit = Circuit[0]

    #             #Store each run time in an array
    #             preprocessing_arr = [None]*rep
    #             run_time_arr = [None]*rep
    #             verifier_time_arr = [None]*rep
    #             broadcastc_size = 0
    #             viewsc_size = 0
    #             broadcast_size = 0
    #             views_size_PR = 0
    #             for repetition in range(rep):
                    
    #                 # Create list of wire data    
    #                 wire_data = circuit.wire_data(n_wires)
    #                 w = Wire(wire_data, n_parties, n_wires)

    #                 #Timing preprocessing
    #                 start_time_preprocessing = time.process_time()

    #                 #Preprocessing - assign lambdas and triples, generate master seeds 
    #                 assign_lambda = p.PRassignLambda(Circuit, w, n_parties)
    #                 triples = assign_lambda[0]
    #                 party_seeds = assign_lambda[1]

    #                 preprocessing_time = time.process_time() - start_time_preprocessing
    #                 preprocessing_arr[repetition] = preprocessing_time

    #                 #Assign v values
    #                 inputs = []
    #                 for i in range(n_input):
    #                     val = Value()
    #                     val.getRand()
    #                     inputs.append(val)

    #                 for i in range(n_input):
    #                     w.set_v(i, inputs[i].splitVal(n_parties))
                                
    #                 #commit round one
    #                 round1 = prover.round_one_internal(n_parties, n_gate, n_input, Circuit, w, party_seeds)
    #                 views_commit = prover.round_one_external(round1)

    #                 #Generate epsilons
    #                 r1 = ''.join(views_commit)
    #                 temp = fs.round2(r1, n_mulgate, n_epsilons)
    #                 epsilon_1 = temp[0]
    #                 epsilon_2 = temp[1]

    #                 start_time = time.process_time()
    #                 #Calculate alpha shares and write e values, v values, e hat values to output wires 
    #                 alpha = circuit.compute_output(Circuit, epsilon_1, epsilon_2, w, n_gate, n_parties, n_epsilons)
    #                 #Compute zeta shares
    #                 zeta = circuit.compute_zeta_share(Circuit, w, alpha, epsilon_1, epsilon_2, n_parties, n_epsilons)
                                
    #                 #commit broadcast
    #                 round3 = prover.round_three_internal(n_parties, n_gate, n_input, n_epsilons, Circuit, w, alpha, zeta)
    #                 broadcast_commit = prover.round_three_external(round3)
    #                 r3 = broadcast_commit
    #                 run_time = time.process_time() - start_time
    #                 run_time_arr[repetition] = run_time
                                
    #                 #Generate parties to corrupt
    #                 n_corrupt = n_parties -1
    #                 parties = fs.round4(r1, r3, n_corrupt, n_parties)

    #                 #round five
    #                 temp = prover.round_five(round1, round3, parties)
    #                 r_broadcast = temp[0]
    #                 broadcast = temp[1]
    #                 r_views = temp[2]
    #                 views = temp[3]

    #                 start_time = time.process_time()
    #                 v.verifier(Circuit, c_info, n_parties, parties, views_commit, views, r_views, broadcast_commit, broadcast, r_broadcast, n_epsilons)
    #                 verifier_time = time.process_time() - start_time
    #                 verifier_time_arr[repetition] = verifier_time

    #                 broadcastc_size += COMMIT_BYTES
    #                 viewsc_size += COMMIT_BYTES*len(views_commit)
    #                 broadcast_size += sum([sum([VALUE_BYTES for v in broadcast[k]]) for k in broadcast if (k!= "alpha" or k!= "zeta")])+sum([VALUE_BYTES for v in broadcast["alpha"] for i in range(n_parties)])*n_epsilons + sum([VALUE_BYTES for v in broadcast["zeta"][0] for i in range(n_parties)])*n_epsilons
    #                 views_size_PR += sum([sum([VALUE_BYTES for v in views[i]["input"]]) for i in range(n_corrupt)]) + SEED_BYTES*n_corrupt

    #             print('number of parties to corrupt:', n_corrupt)
    #             print('number of add gates:', n_addgate)
    #             print('number of mul gates:', n_mulgate)
    #             preprocessing_time = sum(preprocessing_arr)
    #             print('preprocessing time:', preprocessing_time, 'seconds')

    #             run_time = sum(run_time_arr)
    #             print('run time:', run_time, 'seconds')
    #             # Proof size = wire size + circuit size + alpha size + zeta size


    #             print('broadcast commit size:', broadcastc_size)
    #             print('views commit size:', viewsc_size)
    #             print('broadcast size:', broadcast_size)
    #             print('prover views size:', views_size_PR)

    
if __name__ == "__main__": 
    unittest.main(argv=[sys.argv[0]])