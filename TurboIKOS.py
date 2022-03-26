import sys, random, time, unittest
import math, pickle, gmpy2, argparse
from objsize import get_deep_size
from Cryptodome.Util.number import bytes_to_long, long_to_bytes

import circuit, prover, verifier, tree
from gate import gate
from wire import Wire 
from serial import *
import Preprocessing as p
import Fiat_Shamir as fs
from Value import Value

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
                n_sca = temp[-1]
                c_info = temp[10]
                Circuit = temp[0]

                v_circuit = circuit.parse(gate, 1)

                # Create list of wire data
                n_parties = 3    
                wire_data = circuit.wire_data(n_wires)
                w = Wire(wire_data, n_parties, n_wires)

                #Preprocessing - assign lambdas and triples, generate master seeds 
                (party_seeds, root) = tree.make_tree(n_parties)
                party_seeds = party_seeds[:n_parties]
                assign_lambda = p.PRassignLambda(Circuit, w, n_parties, party_seeds)
                triples = assign_lambda[0]

                #Assign v values
                inputs = []
                for i in range(n_input):
                    val = Value()
                    val.getRand()
                    inputs.append(val)

                expected_output = circuit.compute_output_wires(c_info, Circuit, inputs)

                prover_results = prover.run_prover(c_info, Circuit, w, n_parties, inputs, party_seeds, root)

                # v_circuit = circuit.parse(gate, 1)
                verifier.run_verifier(c_info, v_circuit[0], prover_results, expected_output)

                print("passed")
    
    
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
      
                v_circuit = circuit.parse(gate, 1)

                for repetition in range(rep): 
                    # Create list of wire data
                    wire_data = circuit.wire_data(n_wires)
                    w = Wire(wire_data, n_parties, n_wires)

                    #Timing preprocessing
                    start_time_preprocessing = time.process_time()

                    #Preprocessing - assign lambdas and triples, generate master seeds 
                    (party_seeds, root) = tree.make_tree(n_parties)
                    party_seeds = party_seeds[:n_parties]
                    assign_lambda = p.PRassignLambda(Circuit, w, n_parties, party_seeds)
                    triples = assign_lambda[0]

                    #Assign v values
                    inputs = []
                    for i in range(n_input):
                        val = Value()
                        val.getRand()
                        inputs.append(val)

                    #Get preprocessing time
                    preprocessing_time = time.process_time() - start_time_preprocessing
                    preprocessing_arr[repetition] = preprocessing_time

                    expected_output = circuit.compute_output_wires(c_info, Circuit, inputs)

                    prover_results = prover.run_prover(c_info, Circuit, w, n_parties, inputs, party_seeds, root)

                    #Start time for verifier
                    start_time = time.process_time()

                    #verifier test
                    verifier.run_verifier(c_info, v_circuit[0], prover_results, expected_output)

                    #Set time for verifier
                    verifier_time = time.process_time() - start_time
                    verifier_time_arr[repetition] = verifier_time

                    print('prover test passed')

                    # #Calculate size statistics
                    # broadcastc_size += COMMIT_BYTES*3
                    # viewsc_size += COMMIT_BYTES*len(views_committed)
                    # broadcast_size += len(dict_broadcast)
                    # views_size_PR += len(open_views)


                #Print statistics
                #print('number of parties to corrupt:', n_parties - 1)
                # print('number of add gates:', n_gate-n_mul-n_sca)
                # print('number of mul gates:', n_mul)
                # print('number of sca gates:', n_sca)

                # preprocessing_time = sum(preprocessing_arr)
                # print('preprocessing time:', preprocessing_time, 'seconds')

                # run_time = sum(run_time_arr)
                # print('run time:', run_time, 'seconds')
                # # Proof size = wire size + circuit size + alpha size + zeta size

                # print('broadcast commit size:', broadcastc_size)
                # print('views commit size:', viewsc_size)
                # print('broadcast size:', broadcast_size)
                # print('prover views size:', views_size_PR)

                # output_wire = [w.v(w.n_wire-1-i) for i in range(n_output)]
                # flat_output_wires = serial(output_wire)
                # size_output_wires = len(flat_output_wires)

                print("passed")

                # outputs = {'parties': n_parties, 'proof size': size_output_wires + broadcastc_size + broadcast_size + viewsc_size + views_size_PR,'prover time': preprocessing_time + run_time, 'verifier time': sum(verifier_time_arr), \
                #             'preprocessing time': preprocessing_time}

                # return outputs
if __name__ == "__main__": 
    unittest.main(argv=[sys.argv[0]])
