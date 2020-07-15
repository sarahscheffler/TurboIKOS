"""
test cases
"""

import random
import Value
import Preprocessing
# import gate

"""
    Preprocessing.py
"""

"""
correctly verify triples with randomLC
correctly assigns triple to gate
"""
def tripleTest():
    for i in range(50):
        wire_data = [{'lambda': Value.Value()} for i in range(3)]
        circuit = [Preprocessing.gate(0,1,2,operation = 'AND')]
        (gates, wires, tri) = Preprocessing.assignLambda(circuit, wire_data, 3)
        assert(Preprocessing.randomLC(tri))
        assert(gates[0].a.value == sum(wires[0]["lambda"]))
        assert(gates[0].b.value == sum(wires[1]["lambda"]))

