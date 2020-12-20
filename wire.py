from Value import Value

def checkIndex(index, wire):
    assert str(type(index)) == "<class 'int'>"
    assert (index < wire) and (index > -1)

def checkArray(arr, n_parties):
    assert str(type(arr)) == "<class 'list'>"
    assert len(arr) == n_parties
    #for i in arr:
        #assert str(type(i)) == "<class 'int'>"

class Wire:

    def __init__(self, wire_data, n_parties, n_wires): # recieve from circuit.py
        self.data = wire_data
        self.n_wire = n_wires
        self.n_parties = n_parties

    def __repr__(self):
        return "data: " + str(self.data) + " n_wires: " + str(self.n_wire)

    def e(self, index):
        checkIndex(index, self.n_wire)
        return self.data[index]['e']

    def set_e(self, index, val):
        checkIndex(index, self.n_wire)
        self.data[index]['e'] = val
        return 1

    def v(self, index):
        checkIndex(index, self.n_wire)
        return self.data[index]['v']

    def set_v(self, index, arr):
        checkIndex(index, self.n_wire)
        checkArray(arr, self.n_parties)
        self.data[index]['v'] = arr
        return 1

    def lambda_val(self, index):
        checkIndex(index, self.n_wire)
        return self.data[index]['lambda']

    def set_lambda(self, index, arr):
        checkIndex(index, self.n_wire)
        checkArray(arr, self.n_parties)
        self.data[index]['lambda'] = arr
        return 1

    def lam_hat(self, index):
        checkIndex(index, self.n_wire)
        return self.data[index]['lam_hat']

    def set_lam_hat(self, index, arr, mult_count):
        checkIndex(index, self.n_wire)
        checkArray(arr, self.n_parties)
        self.data[index]['lam_hat'][str(mult_count)] = arr
        return 1

    def e_hat(self, index):
        checkIndex(index, self.n_wire)
        return self.data[index]['e_hat']

    def set_e_hat(self, index, val):
        checkIndex(index, self.n_wire)
        self.data[index]['e_hat'] = val
        return 1
