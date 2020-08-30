#from secrets import token_hex  # solid randomness for cryptographic use



# think about optimizing space. e.g shrink randomness from 256-bits to 128-bits used if appropriate.
# change terminology to match circuit.py


from Value import Value
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
