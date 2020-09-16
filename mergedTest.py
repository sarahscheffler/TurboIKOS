import sys
import random
import circuit 
from circuit import n_epsilons
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
                Circuit = circuit.parse(gate, n_parties)
                n_wires = Circuit[4]
                n_gate = Circuit[3]
                l_input = Circuit[1]
                n_input = Circuit[6]
                n_output = Circuit[5]
                l_output = Circuit[2]
                n_mul = Circuit[8]
                c_info = Circuit[10]
                Circuit = Circuit[0]

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
                #Commit round one
                round1 = prover.round_one_internal(n_parties, n_gate, n_input, Circuit, w, party_seeds)
                views_commit = prover.round_one_external(round1)
            
                #Generate epsilonsir
                r1 = ''.join(views_commit)
                temp = fs.round2(r1, n_mul, n_epsilons)
                epsilon_1 = temp[0]
                epsilon_2 = temp[1]
            
                alpha = circuit.compute_output(Circuit, epsilon_1, epsilon_2, w, n_gate, n_parties, n_epsilons)
                m = 0
                for i in range(n_gate):
                    g = Circuit[i]
                    if g.operation == 'AND' or g.operation == 'MUL':
                        for e in range(n_epsilons):
                            for j in range(n_parties):
                                assert(alpha[m][e][j] == epsilon_1[e][m]*w.lambda_val(g.y)[j] + epsilon_2[e][m]*w.lam_hat(g.y)[j])
                        m = m + 1
                
                for j in range(n_gate):
                    g = Circuit[j]
                    #ADD gate
                    if g.operation == 'XOR' or g.operation =='ADD': 
                        #Check v 
                        assert(sum(w.v(g.z)) == (sum(w.v(g.x)) + sum(w.v(g.y))))
                        #Check lambda assignment
                        for i in range(n_parties):
                            assert(w.lambda_val(Circuit[j].x)[i] + w.lambda_val(Circuit[j].y)[i] == w.lambda_val(Circuit[j].z)[i])
                    #MUL gate
                    if g.operation == 'AND' or g.operation == 'MUL':
                        #Check e hat assignment
                        assert(w.e_hat(g.z) == sum(w.lambda_val(g.x)) * sum(w.lam_hat(g.y)) + sum(w.lam_hat(g.z)))
                        #Chck v value
                        assert(sum(w.v(g.z)) == (sum(w.v(g.x)) * sum(w.v(g.y)))) 
                #Check e assignment
                for i in range(n_wires):
                    assert(w.e(i) == sum(w.lambda_val(i)) + sum(w.v(i)))

                zeta = circuit.compute_zeta_share(Circuit, w, alpha, epsilon_1, epsilon_2, n_parties, n_epsilons)
                #Check zeta
                for e in range(n_epsilons):
                    assert(sum(zeta[e]).value == 0)
                #Commit to broadcast
                round3 = prover.round_three_internal(n_parties, n_gate, n_input, n_epsilons, Circuit, w, alpha, zeta)
                broadcast_commit = prover.round_three_external(round3)
                r3 = broadcast_commit
                #number of parties to be corrupted
                t = 2 
                parties = fs.round4(r1, r3, t, n_parties)
            
                #round 5
                temp = prover.round_five(round1, round3, parties)
                r_broadcast = temp[0]
                broadcast = temp[1]
                r_views = temp[2]
                views = temp[3]
                #full_view = viwes of all parties (for debugging)
                full_views = round1[2]
                #r values of all views(for debuggint)
                full_r_views = round1[0]
                #Test prover.py
                #check broadcast and views
                for i in range(n_input):
                    assert(w.e(i) == broadcast['e inputs'][i])
                    for j in range(n_parties):
                        # assert(full_views[j]['input'][i] == w.v(i)[j])
                        # assert(full_views[j]['input lambda'][i] == w.lambda_val(i)[j])
                        pass
            
                m = 0
                for i in range(n_gate):
                    c = Circuit[i]
                    if c.operation == 'MUL' or c.operation == 'AND':
                        for j in range(n_parties):
                            # assert(full_views[j]['lambda z'][m] == w.lambda_val(c.z)[j])
                            # assert(full_views[j]['lambda y hat'][m] == w.lam_hat(c.y)[j])
                            # assert(full_views[j]['lambda z hat'][m] == w.lam_hat(c.z)[j])
                            pass
                    
                        assert(broadcast['e z'][m] == w.e(c.z))
                        assert(broadcast['e z hat'][m] == w.e_hat(c.z))
                        m += 1

                assert(w.v(Circuit[-1].z) == broadcast['output shares']) 
            
                #check commitment of broadcast
                e_inputs_str = b''
                e_z_str = b''
                e_z_hat_str = b''
                alpha_str = b''
                zeta_str = b''
                output_str = b''
            
                for i in range(n_input):
                    e_inputs_str += long_to_bytes(broadcast['e inputs'][i].value)
                for i in range(n_mul):
                    e_z_str += long_to_bytes(broadcast['e z'][i].value)
                    e_z_hat_str += long_to_bytes(broadcast['e z hat'][i].value)
                for i in range(n_parties):
                    for j in range(n_mul):
                        alpha_str += long_to_bytes(broadcast['alpha'][j][i].value)
                    zeta_str += long_to_bytes(broadcast['zeta'][i].value)
                    output_str += long_to_bytes(broadcast['output shares'][i].value)
           
                val = e_inputs_str + e_z_str + e_z_hat_str + alpha_str + zeta_str + output_str
           
                prover.open(r_broadcast, val, broadcast_commit)
            
                #check commitment of views
                for n in range(n_parties):
                    input_str = b''
                    input_lam_str = b''
                    lam_z_str = b''
                    lam_y_hat_str = b''
                    lam_z_hat_str = b''
                    for i in range(n_input):
                        input_str += long_to_bytes(full_views[n]['input'][i].value)
                        # input_lam_str += long_to_bytes(full_views[n]['input lambda'][i].value)
                    for i in range(n_mul):
                        # lam_z_str += long_to_bytes(full_views[n]['lambda z'][i].value)
                        # lam_y_hat_str += long_to_bytes(full_views[n]['lambda y hat'][i].value)
                        # lam_z_hat_str += long_to_bytes(full_views[n]['lambda z hat'][i].value)
                        pass
                    val = input_str + input_lam_str + lam_z_str + lam_y_hat_str + lam_z_hat_str
                    prover.open(full_r_views[n], val, views_commit[n])


                #verifier test
                v.verifier(Circuit, c_info, n_parties, parties, views_commit, views, r_views, broadcast_commit, broadcast, r_broadcast)
                print('prover test passed')


    
    def test_timing_full(self):
        for test in range(1, len(sys.argv)):
            with self.subTest(test = test):
                #Parse circuit
                n_parties = 3    
                Circuit = circuit.parse(gate, n_parties)
                n_wires = Circuit[4]
                n_gate = Circuit[3]
                l_input = Circuit[1]
                n_input = Circuit[6]
                n_output = Circuit[5]
                l_output = Circuit[2]
                n_mulgate = Circuit[8]
                n_parties = Circuit[9]
                c_info = Circuit[10]
                Circuit = Circuit[0]

                #repeat rep times
                rep = 1
                #Store each run time in an array
                preprocessing_arr = [None]*rep
                run_time_arr = [None]*rep
                verifier_time_arr = [None]*rep
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

                    preprocessing_time = time.process_time() - start_time_preprocessing
                    preprocessing_arr[repetition] = preprocessing_time

                    #Assign v values
                    inputs = []
                    for i in range(n_input):
                        val = Value()
                        val.getRand()
                        inputs.append(val)
                   
                    for i in range(n_input):
                        w.set_v(i, inputs[i].splitVal(n_parties))

                    start_time_preprocessing = time.process_time()
                    
                    #commit round one
                    round1 = prover.round_one_internal(n_parties, n_gate, n_input, Circuit, w, party_seeds)
                    views_commit = prover.round_one_external(round1)

                    #TODO: Why is preprocessing_time set twice?
                    preprocessing_time = time.process_time() - start_time_preprocessing
                    preprocessing_arr[repetition] = preprocessing_time

                    #Generate epsilons
                    r1 = ''.join(views_commit)
                    temp = fs.round2(r1, n_mulgate, n_epsilons)
                    epsilon_1 = temp[0]
                    epsilon_2 = temp[1]

                    start_time = time.process_time()
                    #Calculate alpha shares and write e values, v values, e hat values to output wires 
                    alpha = circuit.compute_output(Circuit, epsilon_1, epsilon_2, w, n_gate, n_parties, n_epsilons)
                    #Compute zeta shares
                    zeta = circuit.compute_zeta_share(Circuit, w, alpha, epsilon_1, epsilon_2, n_parties, n_epsilons)
                    
                    #commit broadcast
                    round3 = prover.round_three_internal(n_parties, n_gate, n_input, n_epsilons, Circuit, w, alpha, zeta)
                    broadcast_commit = prover.round_three_external(round3)
                    r3 = broadcast_commit
                    run_time = time.process_time() - start_time
                    run_time_arr[repetition] = run_time
                    
                    #Generate parties to corrupt
                    t = n_parties -1
                    parties = fs.round4(r1, r3, t, n_parties)

                    #round five
                    temp = prover.round_five(round1, round3, parties)
                    r_broadcast = temp[0]
                    broadcast = temp[1]
                    r_views = temp[2]
                    views = temp[3]

                    start_time = time.process_time()
                    v.verifier(Circuit, c_info, n_parties, parties, views_commit, views, r_views, broadcast_commit, broadcast, r_broadcast)
                    verifier_time = time.process_time() - start_time
                    verifier_time_arr[repetition] = verifier_time

                print('number of gates:', n_gate)
                print('number of add gates:', n_gate - n_mulgate)
                print('number of mul gates:', n_mulgate)
                average_preprocessing_time = sum(preprocessing_arr) / rep
                print('average preprocessing time:', average_preprocessing_time, 'seconds')

                average_run_time = sum(run_time_arr) / rep
                print('average run time:', average_run_time, 'seconds')
                # Proof size = wire size + circuit size + alpha size + zeta size
                
                broadcastc_size = get_deep_size(broadcast_commit)
                viewsc_size = get_deep_size(views_commit)
                broadcast_size = get_deep_size(broadcast)
                views_size = get_deep_size(views)
                proof_size = get_deep_size(broadcast_commit) + get_deep_size(views_commit) + get_deep_size(broadcast) + get_deep_size(views)
                print('proof size:', proof_size, 'bytes')
                print('broadcast commit size:', broadcastc_size)
                print('views commit size:', viewsc_size)
                print('broadcast size:', broadcast_size)
                print('views size:', views_size)
                print('timing test passed')
                
    def test_repeat(self):
        for test in range(1, len(sys.argv)):
            with self.subTest(test = test):
                #Parse circuit
                n_parties = int(input('number of parties:'))
                #read in parameter from console and calculate number of repition
                param = int(input('lambda:'))
                rep = math.ceil(math.log(0.5**param, 1/n_parties))
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

                #Store each run time in an array
                preprocessing_arr = [None]*rep
                run_time_arr = [None]*rep
                verifier_time_arr = [None]*rep
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

                    preprocessing_time = time.process_time() - start_time_preprocessing
                    preprocessing_arr[repetition] = preprocessing_time

                    #Assign v values
                    inputs = []
                    for i in range(n_input):
                        val = Value()
                        val.getRand()
                        inputs.append(val)
                               
                    for i in range(n_input):
                        w.set_v(i, inputs[i].splitVal(n_parties))
                                
                    #commit round one
                    round1 = prover.round_one_internal(n_parties, n_gate, n_input, Circuit, w, party_seeds)
                    views_commit = prover.round_one_external(round1)

                    #Generate epsilons
                    r1 = ''.join(views_commit)
                    temp = fs.round2(r1, n_mulgate, n_epsilons)
                    epsilon_1 = temp[0]
                    epsilon_2 = temp[1]

                    start_time = time.process_time()
                    #Calculate alpha shares and write e values, v values, e hat values to output wires 
                    alpha = circuit.compute_output(Circuit, epsilon_1, epsilon_2, w, n_gate, n_parties, n_epsilons)
                    #Compute zeta shares
                    zeta = circuit.compute_zeta_share(Circuit, w, alpha, epsilon_1, epsilon_2, n_parties, n_epsilons)
                                
                    #commit broadcast
                    round3 = prover.round_three_internal(n_parties, n_gate, n_input, n_epsilons, Circuit, w, alpha, zeta)
                    broadcast_commit = prover.round_three_external(round3)
                    r3 = broadcast_commit
                    run_time = time.process_time() - start_time
                    run_time_arr[repetition] = run_time
                                
                    #Generate parties to corrupt
                    n_corrupt = n_parties -1
                    parties = fs.round4(r1, r3, n_corrupt, n_parties)

                    #round five
                    temp = prover.round_five(round1, round3, parties)
                    r_broadcast = temp[0]
                    broadcast = temp[1]
                    r_views = temp[2]
                    views = temp[3]

                    start_time = time.process_time()
                    v.verifier(Circuit, c_info, n_parties, parties, views_commit, views, r_views, broadcast_commit, broadcast, r_broadcast)
                    verifier_time = time.process_time() - start_time
                    verifier_time_arr[repetition] = verifier_time

                print('number of parties to corrupt:', n_corrupt)
                print('number of add gates:', n_addgate)
                print('number of mul gates:', n_mulgate)
                average_preprocessing_time = sum(preprocessing_arr) / rep
                print('average preprocessing time:', average_preprocessing_time, 'seconds')

                average_run_time = sum(run_time_arr) / rep
                print('average run time:', average_run_time, 'seconds')
                # Proof size = wire size + circuit size + alpha size + zeta size

    
if __name__ == "__main__": 
    unittest.main(argv=[sys.argv[0]])
