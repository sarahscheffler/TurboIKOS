"""
a construction of which gates wer will be using. This file is purely for writing functions in the form of logic gates. no data will be stored here)
"""

from Value import Value


'''
# seed the pseudorandom number generator
from random import seed
from random import random
# seed random number generator
seed(1)

# Generate epsilons for testing
epsilon_1 = []*n_parties
epsilon_2 = []*n_parties
for i in range(n_parties):
    epsilon_1[i] = random()
    epsilon_2[i] = random()
'''


class gate:
    # input: 2 inputs, 3 triples/ 0's
    def __init__(self, input1, input2, output, *, triple1=Value(), triple2=Value(), triple3=Value(), operation=None):
        self.operation = operation
        self.x = input1
        self.y = input2
        self.z = output
        if operation == 'AND' or 'MUL':
            self.a = triple1
            self.b = triple2
            self.c = triple3
        if operation == 'XOR' or 'ADD':
            self.a = None
            self.b = None
            self.c = None


'''
    # Assigns v values z = x + y for each party
    # Assign e value on output wire
    def add(self):
        z_v_arr = []*n_parties
        # calculate z_v
        for i in range(n_parties):
            x_v = wire.v(self.x)[i]
            y_v = wire.v(self.y)[i]
            z_v = x_v + y_v
            z_v_arr[i] = z_v
        # set z_v
        wire.set_v(self.z, z_v_arr)
        # calculate z_e
        x_e = wire.e(self.x)
        y_e = wire.e(self.y)
        z_e = x_e + y_e
        # set z_e
        wire.set_e(self.z, z_e)

    # Assigns v values  z = x*y for each party
    # assign e value on output wire
    # return e share for broadcast
    def mult(self):
        #alpha_broadcast = []*circuit.n_parties
        z_v_arr = []*n_parties
        for i in range(n_parties):
            # calculate z_v
            x_e = wire.e(self.x)
            y_e = wire.e(self.y)
            z_v = x_e*y_e - (a[i] * y_e) - (b[i] * x_e) + c[i]
            z_v_arr[i] = z_v
            # calculate alpha share
            y_lam = wire.lambda_val(self.y)[i]
            y_lamh = wire.lambda_hat(self.y)[i]
            #alpha_broadcast[i] = epsilon_1[i]*y_lam + (epsilon_2[i]*y_lamh)

        # set z_v
        wire.set_v(self.z, z_v_arr)

        # calculate and set z_e
        z_e = sum(wire.v(self.z).value) + sum(wire.lambda_val(self.z).value)
        wire.set_e(self.z, Value.value(z_e))

        # calculate and set z_eh
        z_eh = sum(wire.lambda_val(self.x).value) * sum(wire.lambda_hat(self.y).value) + \
            sum(wire.lambda_hat(self.z).value)
        wire.set_eh(self.z, z_eh)

        #return alpha_broadcast
'''
