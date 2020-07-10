
"""
    Value.py
    Wrapper for data type and operations
    - Preprocessing.py
      1. lambda data type
      2. operation to generate Beaver triple
      (3. gate type)
"""

import os
from Cryptodome.Util.number import bytes_to_long
# import pylaurent

"""
    Preprocessing.py
"""

"""
wrapper for lambda data type
"""
def wrapLambda():

    def arithLam():
        return bytes_to_long(os.urandom(16))
    
    return arithLam()

"""
wrapper for operation to generate triple
"""
def wrapOperation(a, b):

    def mul(a, b):
        return a*b

    return mul(a, b)

"""
    Gate.py
"""

"""
wrapper for data calculation
"""

def wrapAdd():
    # return pylaurent addition
    pass

def wrapMul():
    # return pylaurent multiplication
    pass

