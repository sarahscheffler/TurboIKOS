import sys
import random
import circuit 
from gate import gate
from wire import Wire
import Preprocessing as p
from Value import Value

def test():
    Circuit = circuit.parse(gate)
    n_wires = Circuit[4]
    n_gate = Circuit[3]
    l_input = Circuit[1]
    n_input = Circuit[6]
    n_output = Circuit[5]
    l_output = Circuit[2]
    Circuit = Circuit[0]
    print(Circuit[0].x, Circuit[0].y, Circuit[0].z)
    # Create list of wire data
    n_parties = 3    
    wire_data = circuit.wire_data(n_wires)
    w = Wire(wire_data, n_parties, n_wires)
    #Assign v values
    inputs = []
    for i in range(n_input):
        val = Value()
        val.getRand()
        inputs.append(val)
       
    for i in range(n_input):
        w.set_v(i, inputs[i].splitVal(n_parties))
    triples = p.assignLambda(Circuit, w, n_parties)  
    print('0:', w.lambda_val(0))
    print('1:', w.lambda_val(1))
    print('2:', w.lambda_val(2))
    print('3:', w.lambda_val(3))
    circuit.compute_e(Circuit, w, n_gate)     

if __name__ == "__main__": 
    test() 
