
"""
    Value.py
    Wrapper for data type and operations
"""

import os
import gmpy
from gmpy import mpz
from Cryptodome.Util.number import bytes_to_long

class Value:
    def __init__(self, value=None):
        self.value = value

    """
    overload + and sum with ^, * with & for boolean circuit
    overload arithmetic operation with gmpy2 library
    """
    def __add__(self, other, p = 1):
        return Value(self.add(other.value))

    def __radd__(self, other, p = 1):
        return Value(self.add(other))
        
    def __sub__(self, other, p = 1):
        return Value(self.sub(other.value))

    def __mul__(self, other, p = 1):
        return Value(self.mul(other.value))

    """
    support arithmetic operations
    """
    def add(self, num, p = 1):
        return self.value ^ num

    def sub(self, num, p = 1):
        return self.value ^ num
    
    def mul(self, num, p = 1):
        return self.value & num
    
    """
    generate a random number from 128 bit space
    """
    def getRand(self):
        if (not self.value):
            self.value = bytes_to_long(os.urandom(16))

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


            
