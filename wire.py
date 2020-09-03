#from secrets import token_hex  # solid randomness for cryptographic use



# think about optimizing space. e.g shrink randomness from 256-bits to 128-bits used if appropriate.
# change terminology to match circuit.py


from Value import Value
class Wire:

    # Each assertion checks for expected type, length, value, and existence of an object
    def __init__(self, wire_data, n_parties, n_wires): # recieve from circuit.py
        self.data =wire_data
        self.n_wire = n_wires
        self.n_parties = n_parties
        print(n_parties)


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
