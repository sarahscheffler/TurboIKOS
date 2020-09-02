
import sys
from circuit import parse
from gate import gate
from wire import Wire
import Preprocessing as p
from Value import Value

# Parse data
input_stream = sys.argv[1]
with open(input_stream) as f:
    first_line = f.readline().split()
    n_gate = int(first_line[0])
    n_wires = int(first_line[1])
    second_line = f.readline().split()
    n_input = int(second_line[0])
    # create list of number of wires for input value
    l_input = [None]*n_input
    for i in range(n_input):
        l_input[i] = int(second_line[i+1])
    third_line = f.readline().split()
    n_output = int(third_line[0])
    # create list of number of wires for output values
    l_output = [None]*n_output
    for i in range(n_output):
        l_output[i] = int(third_line[i+1])
        # create list of gate
    #circuit = parse(f, n_gate, gate)
    # Create list of wire data
    n_parties = 3
    wire_data = [{'e': None, 'v': []*n_parties, 'lambda': Value(), 'lam_hat':Value(), 'e_hat': None}
                 for i in range(n_wires)]
    Wire(wire_data, n_parties, n_wires)
    circuit = parse(f, n_gate, gate)
    # Generate lambda
    preprocessing = p.assignLambda(circuit, wire_data, n_parties)
    circuit = preprocessing[0]
    wire_data = preprocessing[1]
    triples = preprocessing[2]
    
