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
import math

def full_protocol():
    #Set number of parties
    n_parties = int(input('number of parties:'))
    #read in parameter from console and calculate number of repition 
    param = int(input('lambda:'))
    repetition = math.ceil(math.log(0.5**param, 1/n_parties))

    #parse circuit
    Circuit = circuit.parse(gate)
    n_wires = Circuit[4]
    n_gate = Circuit[3]
    l_input = Circuit[1]
    n_input = Circuit[6]
    n_output = Circuit[5]
    l_output = Circuit[2]
    n_mul = Circuit[8]
    Circuit = Circuit[0]
    
    #create list of wire data
    wire_data = circuit.wire_data(n_wires)
    w = Wire(wire_data, n_parties, n_wires)
    #round 1
    ret = [None]*repetition
    for rep in range(repetition):
        a = []
        #Preprocessing
        triples = p.assignLambda(Circuit, w, n_parties)

        #Assign input values
        inputs = []
        for i in range(n_input):
            val = Value()
            val.getRand()
            inputs.append(val)

        for i in range(n_input):
            w.set_v(i, inputs[i].splitVal(n_parties))
    
        #commit round one
        round1 = prover.round_one_internal(n_parties, n_gate, n_input, Circuit, w)
        views_commit = prover.round_one_external(round1)

        #round2
        #Generate epsilons using fiat shamir
        r1 = ''.join(views_commit)
        temp = fs.round2(r1, n_mul)
        epsilon_1 = temp[0]
        epsilon_2 = temp[1]

        #round3
        #Calculate circuit and alpha
        alpha = circuit.compute_output(Circuit, epsilon_1, epsilon_2, w, n_gate, n_parties)

        #calculate zeta
        zeta = circuit.compute_zeta_share(Circuit, w, alpha, epsilon_1, epsilon_2, n_parties)

        #commit broadcast
        round3 = prover.round_three_internal(n_parties, n_gate, n_input, Circuit, w, alpha, zeta)
        broadcast_commit = prover.round_three_external(round3)
        r3 = broadcast_commit

        #round4
        #number of parties to corrupt
        t = 2
        #generate parties to corrupt using fiat shamir
        parties = fs.round4(r1, r3, t, n_parties)

        #round 5
        #open broadcast and selected views
        temp = prover.round_five(round1, round3, parties)
        r_broadcast = temp[0]
        broadcast = temp[1]
        r_views = temp[2]
        views = temp[3]
        
        ret[rep] = [views_commit, epsilon_1, epsilon_2, broadcast_commit, parties, r_broadcast, broadcast, r_views, views]
        #print
        print('round ', rep+1)
        print('committed views:', views_commit)
        print('epsilons:', epsilon_1)
        print('epsilon hats:', epsilon_2)
        print('committed broadcast:', broadcast_commit)
        print('chosen parties to corrupt', parties)
        print('random values for opening broadcast:', r_broadcast)
        print('opened broadcast:', broadcast)
        print('random values for opening chosen views:', r_views)
        print('opened chosen views:', views)
        print('\n')

    return ret

if __name__ == '__main__':
    full_protocol()
