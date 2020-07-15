
"""
    Value.py
    Wrapper for data type and operations
"""

import os
from Cryptodome.Util.number import bytes_to_long

class Value:
    def __init__(self, value=None):
        self.value = value

    """
    override + and * with ^ and &
    """
    def __add__(self, other):
        return Value(self.add(other.value))
        
    def __sub__(self, other):
        return Value(self.value - other.value)

    def __mul__(self, other):
        return Value(self.mul(other.value))

    """
    support arithmetic operations
    """
    def add(self, num):
        return self.value ^ num
    
    def mul(self, num):
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
            ret.append(bytes_to_long(os.urandom(16)))
        last = self.value - sum(ret)
        ret.append(last)
        return ret

