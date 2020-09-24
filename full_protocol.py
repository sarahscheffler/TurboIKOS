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
from objsize import get_deep_size
import verifier as v
from Cryptodome.Util.number import bytes_to_long, long_to_bytes
import drawTable

COMMIT_BYTES = 32
VALUE_BYTES = 16
SEED_BYTES = int(256/8)
            
def full_protocol():
    prover_time_total = [None]*80
    verifier_time_total = [None]*80
    proof_total = [None]*80
    memory_total = [None]*80

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
    c_info = Circuit[10]
    Circuit = Circuit[0]

    for rep in range(1, 81):
        #Store each run time in an array
        preprocessing_arr = 0
        run_time_arr = 0
        verifier_time_arr = 0
        proof_size = 0
        memory = 0
        
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
            preprocessing_arr += preprocessing_time

            start_time = time.process_time()
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
            temp = fs.round2(r1, n_mulgate)
            epsilon_1 = temp[0]
            epsilon_2 = temp[1]

            #Calculate alpha shares and write e values, v values, e hat values to output wires 
            alpha = circuit.compute_output(Circuit, epsilon_1, epsilon_2, w, n_gate, n_parties)
            #Compute zeta shares
            zeta = circuit.compute_zeta_share(Circuit, w, alpha, epsilon_1, epsilon_2, n_parties)
                            
            #commit broadcast
            round3 = prover.round_three_internal(n_parties, n_gate, n_input, Circuit, w, alpha, zeta)
            broadcast_commit = prover.round_three_external(round3)
            r3 = broadcast_commit
            run_time = time.process_time() - start_time
            run_time_arr += run_time
                        
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
            verifier_time_arr += verifier_time

            broadcastc_size = 0
            viewsc_size = 0
            broadcast_size = 0
            
            broadcastc_size += COMMIT_BYTES
            viewsc_size += COMMIT_BYTES*len(views_commit)
            broadcast_size += sum([sum([VALUE_BYTES for v in broadcast[k]]) for k in broadcast if k!= "alpha"])+sum([VALUE_BYTES for v in broadcast["alpha"] for i in range(n_mulgate)])
            views_size_PR = sum([sum([VALUE_BYTES for v in views[i]["input"]]) for i in range(n_corrupt)]) + SEED_BYTES*n_corrupt

            memory += get_deep_size(broadcast_commit) + get_deep_size(broadcast) + get_deep_size(views_commit) + get_deep_size(views)
            proof_size += broadcastc_size + viewsc_size + broadcast_size + views_size_PR
            
        prover_time_total[rep-1] = preprocessing_arr + run_time_arr
        verifier_time_total[rep-1] = verifier_time_arr
        proof_total[rep-1] = proof_size/(10**6)
        memory_total[rep-1] = memory/(10**6)

    drawTable.tableCompare("%.2f" % proof_total[0], "%.3f" % prover_time_total[0], "%.3f" % verifier_time_total[0], "%.2f" % memory_total[0])
    drawTable.plotTable(prover_time_total, verifier_time_total, proof_total, memory_total)

    return prover_time_total, verifier_time_total, proof_total, memory_total


if __name__ == '__main__':
    full_protocol()
