#from secrets import token_hex  # solid randomness for cryptographic use



# think about optimizing space. e.g shrink randomness from 256-bits to 128-bits used if appropriate.
# change terminology to match circuit.py


from Value import Value
# noinspection DuplicatedCode
class Wire:
    # Each assertion checks for expected type, length, value, and existence of an object
    def __init__(self, wires, n_parties, n_wires): # recieve from circuit.py
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
        self.data = wires
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
        for i in arr:
            assert str(type(i)) == "<class 'int'>"
        assert (index < self.n_wire) and (index > -1)
        self.data[index]['v'] = arr

        return 1

    def lambda_val(self, index):  # cant be named lambda. naming to "l" may result in ambiguousness
        assert str(type(index)) == "<class 'int'>"
        assert (index < self.n_wire) and (index > -1)
        return self.data[index]['v']

    def set_lambda(self, index, arr):
        assert str(type(index)) == "<class 'int'>"
        assert str(type(arr)) == "<class 'list'>"
        assert len(arr) == self.n_parties
        for i in arr:
            assert str(type(i)) == "<class 'int'>"
        assert (index < self.n_wire) and (index > -1)
        self.data[index]['lambda'] = arr
        return 1
    
# def main():
#     n_wires = 3
#     n_parties = 3
#     a = [{'e': 1, 'v': [22] * n_parties, 'lambda': [333] * n_parties}] * n_wires
#     wiredb = Wire(a, n_parties, n_wires)
#     print("Full db: ", wiredb.data)
#     print("db len: ", wiredb.n_wire)
#     teste0_1 = wiredb.e(0)
#     print("e of the first wire: ", teste0_1)
#     wiredb.set_e(0, 3)
#     teste0_3 = wiredb.e(0)
#     print("e of the first wire after using set_e to 3: ", teste0_3)
#     testv0_22 = wiredb.v(0)
#     print("v of first wire: ", testv0_22)
#     wiredb.set_v(0, [44]*n_parties)
#     print("v after wiredb.set_e(0, [44, 44, 44]): ", wiredb.v(0))
#     test_lambda0 = wiredb.lambda_val(0)
#     print("lambdas of the wire0: ", test_lambda0)
#     wiredb.set_lambda(0, [55] * n_parties)
#     test_lambda0_44 = wiredb.lambda_val(0)
#     print("lambdas of the wire0 after setting to [55, 55, 55]: ", test_lambda0_44)
# 
# main()
