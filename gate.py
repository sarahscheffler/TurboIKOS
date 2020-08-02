#ecrets import token_hex  # solid randomness for cryptographic use




# think about optimizing space. e.g shrink randomness from 256-bits to 128-bits used if appropriate.
# change terminology to match circuit.py


from Value import Value
# noinspection DuplicatedCode
class Wire:
    # Each assertion checks for expected type, length, value, and existence of an object
    def __init__(self, wire_data, n_parties, n_wires): # recieve from circuit.py
        '''    
        assert str(type(wires)) == "<class 'list'>"
        assert str(type(n_wires)) == "<class 'int'>"
        assert str(type(n_parties)) == "<class 'int'>"
        assert len(wires) == n_wires
        for j in range(0, n_wires):
            for key in wires[j]:  # check that each party only has e and v and lambda
                assert key == 'e' or key == 'v' or key == 'lambda'
            assert str(type(wires[j])) == "<class 'dict'>"
            assert str(type(wires[j]['e'])) == "<class 'int'>"
            assert str(type(wires[j]['v'])) == "<class 'list'>"
            assert str(type(wires[j]['lambda'])) == "<class 'list'>"
            assert len(wires[j]['v']) == n_parties
            assert len(wires[j]['lambda']) == n_parties
            for k in range(0, n_parties):
                assert str(type(wires[j]['v'][k])) == "<class 'int'>"
                assert str(type(wires[j]['lambda'][k])) == "<class 'int'>"
            assert str(type(wires[j]['lambda'])) == "<class 'list'>"
        '''
        self.data =wire_data
        self.n_wire = n_wires
        self.n_parties = n_parties


    def e(self, index):
        assert str(type(index)) == "<class 'int'>"
        assert (index < self.n_wire) and (index > -1)
        return self.data[index]['e']

    def set_e(self, index, val):
        assert str(type(index)) == "<class 'int'>"
        assert (index < self.n_wire) and (index > -1)
        self.data[index]['e'] = val
        return 1

    def v(self, index):
        assert str(type(index)) == "<class 'int'>"
        assert (index < self.n_wire) and (index > -1)
        return self.data[index]['v']

    def set_v(self, index, arr):
        assert str(type(index)) == "<class 'int'>"
        assert str(type(arr)) == "<class 'list'>"
        assert len(arr) == self.n_parties
        #for i in arr:
            #assert str(type(i)) == "<class 'int'>"
        assert (index < self.n_wire) and (index > -1)
        self.data[index]['v'] = arr

        return 1

    def lambda_val(self, index):  # cant be named lambda. naming to "l" may result in ambiguousness
        assert str(type(index)) == "<class 'int'>"
        assert (index < self.n_wire) and (index > -1)
        return self.data[index]['lambda']

    def set_lambda(self, index, arr):
        assert str(type(index)) == "<class 'int'>"
        assert str(type(arr)) == "<class 'list'>"
        assert len(arr) == self.n_parties
        #for i in arr:
            #assert str(type(i)) == "<class 'int'>"
        assert (index < self.n_wire) and (index > -1)
        self.data[index]['lambda'] = arr
        return 1

    def lam_hat(self, index):
        assert str(type(index)) == "<class 'int'>"
        assert (index < self.n_wire) and (index > -1)
        return self.data[index]['lam_hat']

    def set_lam_hat(self, index, arr):
        assert str(type(index)) == "<class 'int'>"
        assert str(type(arr)) == "<class 'list'>"
        assert len(arr) == self.n_parties
        assert (index < self.n_wire) and (index > -1)
        self.data[index]['lam_hat'] = arr
        return 1

    def e_hat(self, index):
        assert str(type(index)) == "<class 'int'>"
        assert (index < self.n_wire) and (index > -1)
        return self.data[index]['e_hat']

    def set_e_hat(self, index, val):
        assert str(type(index)) == "<class 'int'>"
        assert (index < self.n_wire) and (index > -1)
        self.data[index]['e_hat'] = val
        return 1

class gate:
    # input: 2 inputs, 3 triples/ 0's
    def __init__(self, input1, input2, output,*, wire = None, triple1=Value(), triple2=Value(), triple3=Value(), operation=None):
        self.operation = operation
        self.n_parties = 3
        self.w = wire
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

    # Assigns v values z = x + y for each party
    # Assign e value on output wire
    def add(self):
        z_v_arr = [None]*self.n_parties
        # calculate z_v
        for i in range(self.n_parties):
            x_v = self.w.v(self.x)[i]
            y_v = self.w.v(self.y)[i]
            z_v = x_v + y_v
            z_v_arr[i] = z_v
        # set z_v
        self.w.set_v(self.z, z_v_arr)
        # calculate z_e
        x_e = self.w.e(self.x)
        y_e = self.w.e(self.y)
        if not x_e:
            x_v = sum(self.w.v(self.x))
            x_lam = sum(self.w.lambda_val(self.x)) 
            x_e = (x_v + x_lam)
            self.w.set_e(self.x, x_e)
        if not y_e:
            y_v = sum(self.w.v(self.y))
            y_lam = sum(self.w.lambda_val(self.y))
            y_e = (y_v + y_lam)  
            self.w.set_e(self.y, y_e)
        z_e = x_e + y_e
        # set z_e
        self.w.set_e(self.z, z_e)
    # Assigns v values  z = x*y for each party
    # assign e value on output wire
    # return e share for broadcast
    def mult(self):
        #alpha_broadcast = []*circuit.n_parties
        z_v_arr = [None]*self.n_parties 
        # calculate z_vi
        x_e = self.w.e(self.x)
        y_e = self.w.e(self.y)
        if not x_e:
            x_v = sum(self.w.v(self.x))
            x_lam = sum(self.w.lambda_val(self.x))
            x_e = (x_v + x_lam)
            self.w.set_e(self.x, x_e)
        if not y_e:
            y_v = sum(self.w.v(self.y))
            y_lam = sum(self.w.lambda_val(self.y))
            y_e = (y_v + y_lam)
            self.w.set_e(self.y, y_e)
        #Calculate z_e
        z_v = sum(self.w.v(self.x)) * sum(self.w.v(self.y))
        z_e = z_v + sum(self.w.lambda_val(self.z))
        # calculate and set z_eh
        z_eh = sum(self.w.lambda_val(self.x)) * sum(self.w.lam_hat(self.y)) + \
            sum(self.w.lam_hat(self.z))
        self.w.set_e_hat(self.z, z_eh)
        for i in range(self.n_parties):
            # calculate z_vi
            if i == 0:
                z_v_share = z_e - self.w.lambda_val(self.z)[i]
            else:
                z_v_share = Value(0)-self.w.lambda_val(self.z)[i]
            z_v_arr[i] = z_v_share 
     
          
        self.w.set_v(self.z, z_v_arr)
        # calculate and set z_e
        z_e = sum(self.w.v(self.z)) + sum(self.w.lambda_val(self.z))
        self.w.set_e(self.z, z_e)
       
