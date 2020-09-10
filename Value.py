
"""
    Value.py
    Wrapper for data type and operations
"""

import os
import gmpy2
from gmpy2 import mpz
from Cryptodome.Util.number import bytes_to_long

field = mpz(2**127-1)
r_state = gmpy2.random_state(bytes_to_long(os.urandom(16)))

class Value:
    def __init__(self, value=None):
        self.value = value

    """
    overload + and sum with ^, * with & for boolean circuit
    overload arithmetic operation with gmpy2 library
    """
    def __add__(self, other, p = field):
        return Value(self.add(other.value, p))

    def __radd__(self, other, p = field):
        return Value(self.add(other, p))
        
    def __sub__(self, other, p = field):
        return Value(self.sub(other.value, p))

    def __mul__(self, other, p = field):
        return Value(self.mul(other.value, p))

    """
    overload equality check
    """
    def __eq__(self, other, p = field):
        left = gmpy2.f_mod(self.value, p)
        right = gmpy2.f_mod(other.value, p)
        return left == right

    def __ne__(self, other, p = field):
        left = gmpy2.f_mod(self.value, p)
        right = gmpy2.f_mod(other.value, p)
        return left != right
    '''
    overload print
    '''
    def __repr__(self):
        return str(self.value)

    """
    support arithmetic operations
    """
    def add(self, num, p = field):
        # return self.value ^ num 
        ret = gmpy2.add(self.value, num)
        return gmpy2.f_mod(ret, p)

    def sub(self, num, p = field):
        # return self.value ^ num
        ret = gmpy2.sub(self.value, num)
        return gmpy2.f_mod(ret, p)
    
    def mul(self, num, p = field):
        # return self.value & num
        ret = gmpy2.mul(self.value, num)
        return gmpy2.f_mod(ret, p)
    
    """
    generate a random number from defined field
    """
    def getRand(self, state = r_state):
        if (not self.value):
            # set randomness with seed
            if (not state):
                state = gmpy2.random_state(bytes_to_long(os.urandom(16)))
            self.value = gmpy2.mpz_random(state, field)

    """
    split val into n random shares
    """
    def splitVal(self, n):
        ret = []
        for i in range(n-1):
            temp = Value()
            temp.getRand()
            ret.append(temp)
        last = self - sum(ret)
        ret.append(last)
        return ret
